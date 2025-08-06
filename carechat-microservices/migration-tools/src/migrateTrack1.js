require('dotenv').config();
const { MongoClient } = require('mongodb');
const { Pool } = require('pg');
const winston = require('winston');
const chalk = require('chalk');
const ProgressBar = require('progress');
const { v4: uuidv4 } = require('uuid');
const moment = require('moment');

// Configure logger
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    }),
    new winston.transports.File({ filename: 'migration.log' })
  ]
});

class Track1Migration {
  constructor() {
    this.pgPool = new Pool({
      connectionString: process.env.TRACK1_POSTGRES_URL || 'postgresql://localhost:5432/track1_db'
    });
    
    this.mongoUrl = process.env.MONGODB_URL || 'mongodb://localhost:27017';
    this.dbName = process.env.MONGODB_DATABASE || 'carechat_unified';
    this.mongoClient = null;
    this.db = null;
  }

  async connect() {
    try {
      // Connect to MongoDB
      this.mongoClient = new MongoClient(this.mongoUrl);
      await this.mongoClient.connect();
      this.db = this.mongoClient.db(this.dbName);
      
      logger.info('Connected to MongoDB');
      
      // Test PostgreSQL connection
      await this.pgPool.query('SELECT NOW()');
      logger.info('Connected to PostgreSQL');
      
    } catch (error) {
      logger.error('Connection failed:', error);
      throw error;
    }
  }

  async disconnect() {
    try {
      if (this.mongoClient) {
        await this.mongoClient.close();
      }
      await this.pgPool.end();
      logger.info('Disconnected from databases');
    } catch (error) {
      logger.error('Disconnect error:', error);
    }
  }

  async createCollections() {
    try {
      console.log(chalk.blue('Creating MongoDB collections...'));
      
      // Create collections with validation schemas
      const collections = [
        {
          name: 'users',
          validator: {
            $jsonSchema: {
              bsonType: 'object',
              required: ['userId', 'userType', 'trackOrigin', 'fullName', 'phoneNumber'],
              properties: {
                userId: { bsonType: 'string' },
                userType: { enum: ['patient', 'user', 'admin'] },
                trackOrigin: { enum: ['track1', 'track2'] },
                fullName: { bsonType: 'string' },
                phoneNumber: { bsonType: 'string' },
                email: { bsonType: ['string', 'null'] },
                isActive: { bsonType: 'bool' },
                isVerified: { bsonType: 'bool' },
                createdAt: { bsonType: 'date' },
                updatedAt: { bsonType: 'date' }
              }
            }
          }
        },
        { name: 'conversations' },
        { name: 'messages' },
        { name: 'feedback_sessions' },
        { name: 'reminders' },
        { name: 'reminder_deliveries' },
        { name: 'system_analytics' }
      ];

      for (const collection of collections) {
        try {
          if (collection.validator) {
            await this.db.createCollection(collection.name, {
              validator: collection.validator
            });
          } else {
            await this.db.createCollection(collection.name);
          }
          logger.info(`Created collection: ${collection.name}`);
        } catch (error) {
          if (error.codeName === 'NamespaceExists') {
            logger.info(`Collection ${collection.name} already exists`);
          } else {
            throw error;
          }
        }
      }

      // Create indexes
      await this.createIndexes();
      
    } catch (error) {
      logger.error('Error creating collections:', error);
      throw error;
    }
  }

  async createIndexes() {
    try {
      console.log(chalk.blue('Creating indexes...'));
      
      const indexes = [
        // Users collection
        { collection: 'users', index: { userId: 1 }, unique: true },
        { collection: 'users', index: { phoneNumber: 1 }, unique: true },
        { collection: 'users', index: { email: 1 }, sparse: true, unique: true },
        { collection: 'users', index: { trackOrigin: 1, userType: 1 } },
        
        // Conversations collection
        { collection: 'conversations', index: { conversationId: 1 }, unique: true },
        { collection: 'conversations', index: { userId: 1, trackOrigin: 1 } },
        { collection: 'conversations', index: { lastMessageAt: -1 } },
        
        // Messages collection
        { collection: 'messages', index: { messageId: 1 }, unique: true },
        { collection: 'messages', index: { conversationId: 1, timestamp: 1 } },
        { collection: 'messages', index: { userId: 1, timestamp: -1 } },
        
        // Feedback sessions collection
        { collection: 'feedback_sessions', index: { sessionId: 1 }, unique: true },
        { collection: 'feedback_sessions', index: { userId: 1, createdAt: -1 } },
        
        // Reminders collection
        { collection: 'reminders', index: { reminderId: 1 }, unique: true },
        { collection: 'reminders', index: { userId: 1, status: 1 } },
        { collection: 'reminders', index: { 'schedule.startDate': 1, status: 1 } },
        
        // Reminder deliveries collection
        { collection: 'reminder_deliveries', index: { deliveryId: 1 }, unique: true },
        { collection: 'reminder_deliveries', index: { reminderId: 1, scheduledFor: -1 } },
        { collection: 'reminder_deliveries', index: { userId: 1, status: 1 } }
      ];

      for (const indexConfig of indexes) {
        const options = { ...indexConfig };
        delete options.collection;
        delete options.index;
        
        await this.db.collection(indexConfig.collection).createIndex(
          indexConfig.index, 
          options
        );
        
        logger.info(`Created index on ${indexConfig.collection}: ${JSON.stringify(indexConfig.index)}`);
      }
      
    } catch (error) {
      logger.error('Error creating indexes:', error);
      throw error;
    }
  }

  async migratePatients() {
    try {
      console.log(chalk.green('Migrating patients from Track1...'));
      
      const query = 'SELECT * FROM patients ORDER BY created_at';
      const result = await this.pgPool.query(query);
      const patients = result.rows;
      
      if (patients.length === 0) {
        logger.info('No patients found to migrate');
        return { migrated: 0, errors: 0 };
      }

      const progressBar = new ProgressBar('Migrating patients [:bar] :current/:total (:percent) ETA: :eta s', {
        complete: '=',
        incomplete: ' ',
        width: 40,
        total: patients.length
      });

      let migrated = 0;
      let errors = 0;
      const batchSize = 100;
      
      for (let i = 0; i < patients.length; i += batchSize) {
        const batch = patients.slice(i, i + batchSize);
        const mongoUsers = batch.map(patient => ({
          userId: patient.patient_id,
          userType: 'patient',
          trackOrigin: 'track1',
          fullName: patient.full_name,
          phoneNumber: patient.phone_number,
          email: patient.email || null,
          preferredLanguage: patient.preferred_language || 'en',
          passwordHash: patient.password_hash,
          
          profile: {
            patientId: patient.patient_id,
            medicalInfo: {
              conditions: patient.medical_conditions ? patient.medical_conditions.split(',') : [],
              allergies: patient.allergies ? patient.allergies.split(',') : [],
              medications: patient.medications ? patient.medications.split(',') : []
            }
          },
          
          isActive: patient.is_active !== false,
          isVerified: patient.is_verified || false,
          lastLogin: patient.last_login,
          
          createdAt: patient.created_at,
          updatedAt: patient.updated_at,
          migratedFrom: {
            source: 'postgresql_track1',
            originalId: patient.patient_id,
            migratedAt: new Date()
          }
        }));

        try {
          await this.db.collection('users').insertMany(mongoUsers, { ordered: false });
          migrated += mongoUsers.length;
        } catch (error) {
          if (error.writeErrors) {
            migrated += mongoUsers.length - error.writeErrors.length;
            errors += error.writeErrors.length;
          } else {
            errors += mongoUsers.length;
            logger.error('Batch insert error:', error);
          }
        }

        // Update progress bar
        progressBar.tick(batch.length);
      }

      console.log(chalk.green(`\nPatients migration completed: ${migrated} migrated, ${errors} errors`));
      return { migrated, errors };
      
    } catch (error) {
      logger.error('Error migrating patients:', error);
      throw error;
    }
  }

  async migrateFeedback() {
    try {
      console.log(chalk.green('Migrating feedback from Track1...'));
      
      const query = `
        SELECT f.*, p.patient_id as user_id, p.full_name as patient_name
        FROM feedback f
        LEFT JOIN patients p ON f.patient_id = p.patient_id
        ORDER BY f.created_at
      `;
      const result = await this.pgPool.query(query);
      const feedbacks = result.rows;
      
      if (feedbacks.length === 0) {
        logger.info('No feedback found to migrate');
        return { migrated: 0, errors: 0 };
      }

      const progressBar = new ProgressBar('Migrating feedback [:bar] :current/:total (:percent) ETA: :eta s', {
        complete: '=',
        incomplete: ' ',
        width: 40,
        total: feedbacks.length
      });

      let migrated = 0;
      let errors = 0;
      const batchSize = 50;
      
      for (let i = 0; i < feedbacks.length; i += batchSize) {
        const batch = feedbacks.slice(i, i + batchSize);
        const operations = [];
        
        for (const feedback of batch) {
          // Create conversation for this feedback
          const conversationId = uuidv4();
          const messageId = uuidv4();
          const sessionId = uuidv4();
          
          // Conversation document
          operations.push({
            insertOne: {
              document: {
                conversationId,
                userId: feedback.user_id,
                trackOrigin: 'track1',
                conversationType: 'feedback',
                title: `Feedback - ${feedback.department || 'General'}`,
                status: 'archived',
                messageCount: 1,
                startedAt: feedback.created_at,
                lastMessageAt: feedback.created_at,
                archivedAt: feedback.created_at,
                createdAt: feedback.created_at,
                updatedAt: feedback.updated_at
              }
            }
          });
          
          // Message document
          operations.push({
            insertOne: {
              document: {
                messageId,
                conversationId,
                userId: feedback.user_id,
                role: 'user',
                content: feedback.message,
                contentType: 'feedback',
                originalLanguage: feedback.language || 'en',
                
                feedbackAnalysis: {
                  rating: feedback.rating,
                  sentiment: feedback.sentiment,
                  sentimentScore: feedback.sentiment_score,
                  topics: feedback.topics ? feedback.topics.split(',') : [],
                  urgency: feedback.urgency,
                  urgencyScore: feedback.urgency_score,
                  actionRequired: feedback.action_required || false,
                  department: feedback.department,
                  category: feedback.category
                },
                
                timestamp: feedback.created_at,
                createdAt: feedback.created_at,
                updatedAt: feedback.updated_at
              }
            }
          });
          
          // Feedback session document
          operations.push({
            insertOne: {
              document: {
                sessionId,
                userId: feedback.user_id,
                conversationId,
                sessionType: 'general',
                department: feedback.department,
                
                overallRating: feedback.rating,
                overallSentiment: feedback.sentiment,
                
                responses: [{
                  questionId: 'general_feedback',
                  question: 'How was your experience?',
                  responseType: 'text',
                  response: feedback.message,
                  rating: feedback.rating,
                  sentiment: feedback.sentiment,
                  topics: feedback.topics ? feedback.topics.split(',') : [],
                  urgency: feedback.urgency
                }],
                
                analytics: {
                  completionRate: 100,
                  satisfactionIndex: feedback.rating * 20, // Convert 1-5 to 0-100
                  actionItems: feedback.action_required ? ['Follow up required'] : [],
                  followUpRequired: feedback.action_required || false,
                  escalationLevel: feedback.urgency === 'high' ? 2 : feedback.urgency === 'medium' ? 1 : 0
                },
                
                language: feedback.language || 'en',
                status: 'completed',
                reviewStatus: feedback.action_required ? 'pending' : 'reviewed',
                
                createdAt: feedback.created_at,
                updatedAt: feedback.updated_at,
                submittedAt: feedback.created_at
              }
            }
          });
        }

        try {
          // Insert conversations
          const conversationOps = operations.filter(op => op.insertOne.document.conversationId);
          if (conversationOps.length > 0) {
            await this.db.collection('conversations').bulkWrite(conversationOps.slice(0, conversationOps.length / 3));
          }
          
          // Insert messages
          const messageOps = operations.filter(op => op.insertOne.document.messageId);
          if (messageOps.length > 0) {
            await this.db.collection('messages').bulkWrite(messageOps.slice(0, messageOps.length / 3));
          }
          
          // Insert feedback sessions
          const sessionOps = operations.filter(op => op.insertOne.document.sessionId);
          if (sessionOps.length > 0) {
            await this.db.collection('feedback_sessions').bulkWrite(sessionOps);
          }
          
          migrated += batch.length;
        } catch (error) {
          errors += batch.length;
          logger.error('Batch insert error for feedback:', error);
        }

        progressBar.tick(batch.length);
      }

      console.log(chalk.green(`\nFeedback migration completed: ${migrated} migrated, ${errors} errors`));
      return { migrated, errors };
      
    } catch (error) {
      logger.error('Error migrating feedback:', error);
      throw error;
    }
  }

  async migrateReminders() {
    try {
      console.log(chalk.green('Migrating reminders from Track1...'));
      
      const query = `
        SELECT r.*, p.patient_id as user_id
        FROM reminders r
        LEFT JOIN patients p ON r.patient_id = p.patient_id
        ORDER BY r.created_at
      `;
      const result = await this.pgPool.query(query);
      const reminders = result.rows;
      
      if (reminders.length === 0) {
        logger.info('No reminders found to migrate');
        return { migrated: 0, errors: 0 };
      }

      const progressBar = new ProgressBar('Migrating reminders [:bar] :current/:total (:percent) ETA: :eta s', {
        complete: '=',
        incomplete: ' ',
        width: 40,
        total: reminders.length
      });

      let migrated = 0;
      let errors = 0;
      const batchSize = 100;
      
      for (let i = 0; i < reminders.length; i += batchSize) {
        const batch = reminders.slice(i, i + batchSize);
        const mongoReminders = batch.map(reminder => ({
          reminderId: reminder.reminder_id,
          userId: reminder.user_id,
          
          title: reminder.title,
          message: reminder.message,
          reminderType: reminder.reminder_type || 'custom',
          category: reminder.category,
          
          schedule: {
            type: reminder.is_recurring ? 'recurring' : 'one_time',
            startDate: reminder.start_date,
            endDate: reminder.end_date,
            scheduledTime: reminder.scheduled_time,
            
            recurrence: reminder.is_recurring ? {
              pattern: reminder.recurrence_pattern || 'daily',
              interval: reminder.recurrence_interval || 1,
              times: reminder.reminder_times ? reminder.reminder_times.split(',') : ['09:00']
            } : null
          },
          
          delivery: {
            methods: reminder.delivery_methods ? reminder.delivery_methods.split(',') : ['sms'],
            preferences: {
              sms: { 
                phone: reminder.phone_number,
                enabled: reminder.sms_enabled !== false
              },
              email: {
                address: reminder.email_address,
                enabled: reminder.email_enabled !== false
              }
            },
            retryPolicy: {
              maxRetries: 3,
              retryInterval: 15,
              backoffMultiplier: 2
            }
          },
          
          smartFeatures: {
            adaptiveScheduling: false,
            contextAwareness: false,
            escalationRules: []
          },
          
          status: reminder.is_active ? 'active' : 'cancelled',
          analytics: {
            totalScheduled: 0,
            totalSent: 0,
            totalDelivered: 0,
            totalAcknowledged: 0,
            responseRate: 0,
            avgResponseTime: 0,
            missedConsecutive: 0
          },
          
          createdAt: reminder.created_at,
          updatedAt: reminder.updated_at,
          createdBy: reminder.created_by
        }));

        try {
          await this.db.collection('reminders').insertMany(mongoReminders, { ordered: false });
          migrated += mongoReminders.length;
        } catch (error) {
          if (error.writeErrors) {
            migrated += mongoReminders.length - error.writeErrors.length;
            errors += error.writeErrors.length;
          } else {
            errors += mongoReminders.length;
            logger.error('Batch insert error:', error);
          }
        }

        progressBar.tick(batch.length);
      }

      console.log(chalk.green(`\nReminders migration completed: ${migrated} migrated, ${errors} errors`));
      return { migrated, errors };
      
    } catch (error) {
      logger.error('Error migrating reminders:', error);
      throw error;
    }
  }

  async migrateReminderDeliveries() {
    try {
      console.log(chalk.green('Migrating reminder deliveries from Track1...'));
      
      const query = `
        SELECT rd.*, r.reminder_id, r.patient_id as user_id
        FROM reminder_delivery rd
        LEFT JOIN reminders r ON rd.reminder_id = r.reminder_id
        ORDER BY rd.created_at
      `;
      const result = await this.pgPool.query(query);
      const deliveries = result.rows;
      
      if (deliveries.length === 0) {
        logger.info('No reminder deliveries found to migrate');
        return { migrated: 0, errors: 0 };
      }

      const progressBar = new ProgressBar('Migrating deliveries [:bar] :current/:total (:percent) ETA: :eta s', {
        complete: '=',
        incomplete: ' ',
        width: 40,
        total: deliveries.length
      });

      let migrated = 0;
      let errors = 0;
      const batchSize = 200;
      
      for (let i = 0; i < deliveries.length; i += batchSize) {
        const batch = deliveries.slice(i, i + batchSize);
        const mongoDeliveries = batch.map(delivery => ({
          deliveryId: delivery.delivery_id,
          reminderId: delivery.reminder_id,
          userId: delivery.user_id,
          
          scheduledFor: delivery.scheduled_for,
          sentAt: delivery.sent_at,
          deliveredAt: delivery.delivered_at,
          acknowledgedAt: delivery.acknowledged_at,
          
          method: delivery.delivery_method || 'sms',
          status: delivery.status,
          
          provider: {
            name: delivery.provider_name,
            messageId: delivery.provider_message_id,
            response: delivery.provider_response ? JSON.parse(delivery.provider_response) : {},
            cost: delivery.cost || 0,
            errorCode: delivery.error_code,
            errorMessage: delivery.error_message
          },
          
          userResponse: {
            acknowledged: delivery.acknowledged_at ? true : false,
            responseTime: delivery.response_time,
            feedback: delivery.user_feedback,
            actionTaken: delivery.action_taken
          },
          
          retryCount: delivery.retry_count || 0,
          maxRetries: 3,
          finalAttempt: delivery.is_final_attempt || false,
          
          context: {
            userTimezone: delivery.user_timezone,
            deviceType: delivery.device_type
          },
          
          createdAt: delivery.created_at,
          updatedAt: delivery.updated_at
        }));

        try {
          await this.db.collection('reminder_deliveries').insertMany(mongoDeliveries, { ordered: false });
          migrated += mongoDeliveries.length;
        } catch (error) {
          if (error.writeErrors) {
            migrated += mongoDeliveries.length - error.writeErrors.length;
            errors += error.writeErrors.length;
          } else {
            errors += mongoDeliveries.length;
            logger.error('Batch insert error:', error);
          }
        }

        progressBar.tick(batch.length);
      }

      console.log(chalk.green(`\nReminder deliveries migration completed: ${migrated} migrated, ${errors} errors`));
      return { migrated, errors };
      
    } catch (error) {
      logger.error('Error migrating reminder deliveries:', error);
      throw error;
    }
  }

  async run() {
    console.log(chalk.blue.bold('\n🚀 Starting Track1 to MongoDB Migration\n'));
    
    try {
      await this.connect();
      await this.createCollections();
      
      const results = {
        patients: await this.migratePatients(),
        feedback: await this.migrateFeedback(),
        reminders: await this.migrateReminders(),
        reminderDeliveries: await this.migrateReminderDeliveries()
      };
      
      console.log(chalk.green.bold('\n✅ Migration Summary:'));
      console.log(chalk.green(`Patients: ${results.patients.migrated} migrated, ${results.patients.errors} errors`));
      console.log(chalk.green(`Feedback: ${results.feedback.migrated} migrated, ${results.feedback.errors} errors`));
      console.log(chalk.green(`Reminders: ${results.reminders.migrated} migrated, ${results.reminders.errors} errors`));
      console.log(chalk.green(`Deliveries: ${results.reminderDeliveries.migrated} migrated, ${results.reminderDeliveries.errors} errors`));
      
      const totalMigrated = Object.values(results).reduce((sum, r) => sum + r.migrated, 0);
      const totalErrors = Object.values(results).reduce((sum, r) => sum + r.errors, 0);
      
      console.log(chalk.blue.bold(`\nTotal: ${totalMigrated} records migrated, ${totalErrors} errors`));
      
      if (totalErrors === 0) {
        console.log(chalk.green.bold('🎉 Migration completed successfully!'));
      } else {
        console.log(chalk.yellow.bold('⚠️  Migration completed with some errors. Please check the logs.'));
      }
      
    } catch (error) {
      console.log(chalk.red.bold('❌ Migration failed:'), error.message);
      logger.error('Migration failed:', error);
      throw error;
    } finally {
      await this.disconnect();
    }
  }
}

// Run migration if called directly
if (require.main === module) {
  const migration = new Track1Migration();
  migration.run().catch(error => {
    console.error(chalk.red('Migration failed:'), error);
    process.exit(1);
  });
}

module.exports = Track1Migration;

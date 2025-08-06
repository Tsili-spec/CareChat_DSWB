const express = require('express');
const router = express.Router();
const { body, validationResult } = require('express-validator');
const { v4: uuidv4 } = require('uuid');
const moment = require('moment');
const Sentiment = require('sentiment');
const nlp = require('compromise');

const logger = require('../utils/logger');
const { asyncHandler } = require('../middleware/errorHandler');

const sentiment = new Sentiment();

/**
 * @route   GET /feedback
 * @desc    Get feedback sessions for a user
 * @access  Private
 */
router.get('/', asyncHandler(async (req, res) => {
  const { page = 1, limit = 20, status, department, userId } = req.query;
  const db = req.app.locals.db;
  
  // Build query
  const query = {};
  
  // Filter by user if not admin
  if (req.user.userType !== 'admin') {
    query.userId = req.user.userId;
  } else if (userId) {
    query.userId = userId;
  }
  
  if (status) query.status = status;
  if (department) query.department = department;
  
  // Pagination
  const skip = (parseInt(page) - 1) * parseInt(limit);
  
  const [sessions, total] = await Promise.all([
    db.collection('feedback_sessions')
      .find(query)
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(parseInt(limit))
      .toArray(),
    db.collection('feedback_sessions').countDocuments(query)
  ]);
  
  res.json({
    sessions,
    pagination: {
      currentPage: parseInt(page),
      totalPages: Math.ceil(total / parseInt(limit)),
      totalSessions: total,
      limit: parseInt(limit)
    }
  });
}));

/**
 * @route   GET /feedback/:sessionId
 * @desc    Get specific feedback session
 * @access  Private
 */
router.get('/:sessionId', asyncHandler(async (req, res) => {
  const { sessionId } = req.params;
  const db = req.app.locals.db;
  
  const session = await db.collection('feedback_sessions').findOne({
    sessionId,
    ...(req.user.userType !== 'admin' && { userId: req.user.userId })
  });
  
  if (!session) {
    return res.status(404).json({
      error: 'Session not found',
      message: 'Feedback session not found or access denied'
    });
  }
  
  res.json(session);
}));

/**
 * @route   POST /feedback
 * @desc    Create new feedback session
 * @access  Private
 */
router.post('/', [
  body('sessionType').isIn(['post_visit', 'medication', 'service_quality', 'general']),
  body('department').optional().isString().trim(),
  body('responses').isArray().withMessage('Responses must be an array'),
  body('responses.*.question').isString().withMessage('Question is required'),
  body('responses.*.response').notEmpty().withMessage('Response is required'),
  body('responses.*.rating').optional().isInt({ min: 1, max: 5 })
], asyncHandler(async (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      error: 'Validation Error',
      details: errors.array()
    });
  }
  
  const {
    sessionType,
    department,
    visitDate,
    visitType,
    responses,
    language = 'en'
  } = req.body;
  
  const db = req.app.locals.db;
  const sessionId = uuidv4();
  const conversationId = uuidv4();
  
  // Process responses with AI analysis
  const processedResponses = await Promise.all(responses.map(async (response) => {
    const analysisResult = await analyzeResponse(response.response);
    
    return {
      questionId: response.questionId || uuidv4(),
      question: response.question,
      responseType: response.responseType || 'text',
      response: response.response,
      rating: response.rating,
      sentiment: analysisResult.sentiment,
      sentimentScore: analysisResult.sentimentScore,
      topics: analysisResult.topics,
      urgency: analysisResult.urgency,
      urgencyScore: analysisResult.urgencyScore
    };
  }));
  
  // Calculate overall metrics
  const ratings = processedResponses.filter(r => r.rating).map(r => r.rating);
  const overallRating = ratings.length > 0 ? Math.round(ratings.reduce((a, b) => a + b, 0) / ratings.length) : null;
  
  const sentiments = processedResponses.map(r => r.sentiment).filter(Boolean);
  const overallSentiment = sentiments.length > 0 ? getMostFrequent(sentiments) : 'neutral';
  
  const allTopics = processedResponses.flatMap(r => r.topics || []);
  const uniqueTopics = [...new Set(allTopics)];
  
  // Determine urgency and escalation
  const maxUrgencyScore = Math.max(...processedResponses.map(r => r.urgencyScore || 0));
  const urgencyLevel = maxUrgencyScore > 0.7 ? 'high' : maxUrgencyScore > 0.4 ? 'medium' : 'low';
  const escalationLevel = maxUrgencyScore > 0.8 ? 3 : maxUrgencyScore > 0.6 ? 2 : maxUrgencyScore > 0.4 ? 1 : 0;
  
  // Create feedback session
  const feedbackSession = {
    sessionId,
    userId: req.user.userId,
    conversationId,
    
    sessionType,
    department: department || 'general',
    visitDate: visitDate ? new Date(visitDate) : null,
    visitType,
    
    overallRating,
    overallSentiment,
    recommendationScore: overallRating ? overallRating * 2 : null, // Convert 1-5 to 0-10
    
    responses: processedResponses,
    
    analytics: {
      completionRate: (processedResponses.length / responses.length) * 100,
      timeSpent: 0, // Could be tracked on frontend
      satisfactionIndex: overallRating ? overallRating * 20 : null, // Convert to 0-100
      actionItems: generateActionItems(processedResponses),
      followUpRequired: escalationLevel >= 2,
      escalationLevel
    },
    
    language,
    status: 'completed',
    reviewStatus: escalationLevel >= 2 ? 'pending' : 'reviewed',
    
    createdAt: new Date(),
    updatedAt: new Date(),
    submittedAt: new Date()
  };
  
  // Create conversation record
  const conversation = {
    conversationId,
    userId: req.user.userId,
    trackOrigin: 'track1',
    conversationType: 'feedback',
    title: `Feedback - ${department || 'General'}`,
    status: 'completed',
    messageCount: processedResponses.length,
    startedAt: new Date(),
    lastMessageAt: new Date(),
    createdAt: new Date(),
    updatedAt: new Date()
  };
  
  // Create message records for each response
  const messages = processedResponses.map((response, index) => ({
    messageId: uuidv4(),
    conversationId,
    userId: req.user.userId,
    role: 'user',
    content: response.response,
    contentType: 'feedback',
    originalLanguage: language,
    
    feedbackAnalysis: {
      rating: response.rating,
      sentiment: response.sentiment,
      sentimentScore: response.sentimentScore,
      topics: response.topics,
      urgency: urgencyLevel,
      urgencyScore: response.urgencyScore,
      actionRequired: escalationLevel >= 2,
      department: department || 'general',
      category: sessionType
    },
    
    timestamp: new Date(),
    createdAt: new Date(),
    updatedAt: new Date()
  }));
  
  // Insert all records
  await Promise.all([
    db.collection('feedback_sessions').insertOne(feedbackSession),
    db.collection('conversations').insertOne(conversation),
    db.collection('messages').insertMany(messages)
  ]);
  
  logger.info('Feedback session created', {
    sessionId,
    userId: req.user.userId,
    sessionType,
    overallRating,
    escalationLevel
  });
  
  res.status(201).json({
    sessionId,
    conversationId,
    status: 'completed',
    overallRating,
    overallSentiment,
    escalationLevel,
    followUpRequired: feedbackSession.analytics.followUpRequired,
    createdAt: feedbackSession.createdAt
  });
}));

/**
 * @route   PUT /feedback/:sessionId
 * @desc    Update feedback session (for staff reviews)
 * @access  Private (Admin only)
 */
router.put('/:sessionId', [
  body('reviewStatus').optional().isIn(['pending', 'reviewed', 'acted_upon']),
  body('assignedTo').optional().isString(),
  body('staffNotes').optional().isString()
], asyncHandler(async (req, res) => {
  if (req.user.userType !== 'admin') {
    return res.status(403).json({
      error: 'Access Denied',
      message: 'Only admin users can update feedback sessions'
    });
  }
  
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({
      error: 'Validation Error',
      details: errors.array()
    });
  }
  
  const { sessionId } = req.params;
  const { reviewStatus, assignedTo, staffNotes } = req.body;
  const db = req.app.locals.db;
  
  const updateData = {
    updatedAt: new Date()
  };
  
  if (reviewStatus) updateData.reviewStatus = reviewStatus;
  if (assignedTo) updateData.assignedTo = assignedTo;
  if (staffNotes) updateData.staffNotes = staffNotes;
  if (reviewStatus === 'reviewed' || reviewStatus === 'acted_upon') {
    updateData.reviewedAt = new Date();
  }
  
  const result = await db.collection('feedback_sessions').updateOne(
    { sessionId },
    { $set: updateData }
  );
  
  if (result.matchedCount === 0) {
    return res.status(404).json({
      error: 'Session not found',
      message: 'Feedback session not found'
    });
  }
  
  logger.info('Feedback session updated', {
    sessionId,
    updatedBy: req.user.userId,
    reviewStatus,
    assignedTo
  });
  
  res.json({
    message: 'Feedback session updated successfully',
    sessionId,
    updatedFields: Object.keys(updateData)
  });
}));

/**
 * @route   GET /feedback/analytics/summary
 * @desc    Get feedback analytics summary
 * @access  Private (Admin only)
 */
router.get('/analytics/summary', asyncHandler(async (req, res) => {
  if (req.user.userType !== 'admin') {
    return res.status(403).json({
      error: 'Access Denied',
      message: 'Only admin users can access analytics'
    });
  }
  
  const { startDate, endDate, department } = req.query;
  const db = req.app.locals.db;
  
  // Build query
  const query = {};
  if (startDate || endDate) {
    query.createdAt = {};
    if (startDate) query.createdAt.$gte = new Date(startDate);
    if (endDate) query.createdAt.$lte = new Date(endDate);
  }
  if (department) query.department = department;
  
  const [
    totalSessions,
    avgRating,
    sentimentDistribution,
    departmentStats,
    urgencyStats
  ] = await Promise.all([
    // Total sessions
    db.collection('feedback_sessions').countDocuments(query),
    
    // Average rating
    db.collection('feedback_sessions').aggregate([
      { $match: { ...query, overallRating: { $exists: true, $ne: null } } },
      { $group: { _id: null, avgRating: { $avg: '$overallRating' } } }
    ]).toArray(),
    
    // Sentiment distribution
    db.collection('feedback_sessions').aggregate([
      { $match: query },
      { $group: { _id: '$overallSentiment', count: { $sum: 1 } } }
    ]).toArray(),
    
    // Department statistics
    db.collection('feedback_sessions').aggregate([
      { $match: query },
      {
        $group: {
          _id: '$department',
          count: { $sum: 1 },
          avgRating: { $avg: '$overallRating' },
          avgSatisfaction: { $avg: '$analytics.satisfactionIndex' }
        }
      }
    ]).toArray(),
    
    // Urgency statistics
    db.collection('feedback_sessions').aggregate([
      { $match: query },
      { $group: { _id: '$analytics.escalationLevel', count: { $sum: 1 } } }
    ]).toArray()
  ]);
  
  res.json({
    summary: {
      totalSessions,
      averageRating: avgRating[0]?.avgRating || 0,
      responseRate: 85, // Could be calculated based on sent vs received
    },
    distributions: {
      sentiment: sentimentDistribution,
      departments: departmentStats,
      urgency: urgencyStats
    },
    dateRange: {
      startDate: startDate || null,
      endDate: endDate || null
    }
  });
}));

// Helper functions
async function analyzeResponse(text) {
  try {
    // Sentiment analysis
    const sentimentResult = sentiment.analyze(text);
    const sentimentScore = sentimentResult.score / Math.max(1, Math.abs(sentimentResult.score));
    const sentimentLabel = sentimentScore > 0.1 ? 'positive' : 
                          sentimentScore < -0.1 ? 'negative' : 'neutral';
    
    // Topic extraction using NLP
    const doc = nlp(text);
    const topics = [
      ...doc.topics().out('array'),
      ...doc.nouns().out('array')
    ].filter(topic => topic.length > 2).slice(0, 5); // Top 5 topics
    
    // Urgency detection
    const urgencyKeywords = ['urgent', 'emergency', 'immediately', 'asap', 'critical', 'serious'];
    const urgencyScore = urgencyKeywords.some(keyword => 
      text.toLowerCase().includes(keyword)
    ) ? 0.8 : Math.abs(sentimentScore) > 0.5 ? 0.6 : 0.2;
    
    return {
      sentiment: sentimentLabel,
      sentimentScore,
      topics,
      urgency: urgencyScore > 0.6 ? 'high' : urgencyScore > 0.3 ? 'medium' : 'low',
      urgencyScore
    };
  } catch (error) {
    logger.error('Error analyzing response:', error);
    return {
      sentiment: 'neutral',
      sentimentScore: 0,
      topics: [],
      urgency: 'low',
      urgencyScore: 0
    };
  }
}

function getMostFrequent(arr) {
  const frequency = {};
  arr.forEach(item => {
    frequency[item] = (frequency[item] || 0) + 1;
  });
  
  return Object.keys(frequency).reduce((a, b) => 
    frequency[a] > frequency[b] ? a : b
  );
}

function generateActionItems(responses) {
  const actionItems = [];
  
  responses.forEach(response => {
    if (response.urgencyScore > 0.6) {
      actionItems.push(`Follow up on: ${response.question}`);
    }
    if (response.rating && response.rating <= 2) {
      actionItems.push(`Address low rating for: ${response.question}`);
    }
  });
  
  return actionItems.slice(0, 3); // Limit to top 3 action items
}

module.exports = router;

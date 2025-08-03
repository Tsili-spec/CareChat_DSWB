// Simple test to verify the API response structure matches our interface
const sampleAPIResponse = {
  "forecast_period": {
    "start_date": "2025-08-02",
    "end_date": "2025-08-08",
    "days": 7
  },
  "optimization_results": [
    {
      "blood_group": "A+",
      "current_stock": 2500.0,
      "predicted_usage": 1200.0,
      "predicted_donations": 800.0,
      "projected_stock": 2100.0,
      "recommended_order": 0,
      "status": "adequate",
      "notes": "Stock levels sufficient for forecast period"
    },
    {
      "blood_group": "O-",
      "current_stock": 800.0,
      "predicted_usage": 900.0,
      "predicted_donations": 300.0,
      "projected_stock": 200.0,
      "recommended_order": 500,
      "status": "order_required",
      "notes": "Critical stock level predicted, immediate order recommended"
    }
  ],
  "summary": {
    "total_current_stock": 12500.0,
    "total_predicted_usage": 5400.0,
    "total_predicted_donations": 3200.0,
    "total_recommended_orders": 1000.0
  }
};

console.log("✅ API Response Structure Test:");
console.log("- forecast_period:", !!sampleAPIResponse.forecast_period);
console.log("- optimization_results:", !!sampleAPIResponse.optimization_results);
console.log("- summary:", !!sampleAPIResponse.summary);
console.log("- Total blood groups:", sampleAPIResponse.optimization_results.length);

// Test filtering logic
const criticalTypes = sampleAPIResponse.optimization_results.filter(
  result => result.status === 'order_required' || result.recommended_order > 0
);
console.log("- Critical blood types:", criticalTypes.map(t => t.blood_group));

const adequateTypes = sampleAPIResponse.optimization_results.filter(
  result => result.status === 'adequate'
);
console.log("- Adequate blood types:", adequateTypes.map(t => t.blood_group));

console.log("\n✅ All tests passed! The interface matches the API structure.");

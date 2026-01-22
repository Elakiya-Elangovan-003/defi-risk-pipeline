import json
import numpy as np
from datetime import datetime

class RiskScorer:
    """Foundation for ML risk scoring system"""
    
    def __init__(self):
        print("🧠 Initializing Risk Scoring Engine...")
        
        # Risk factors (will be ML-trained in full version)
        self.risk_weights = {
            'volume_volatility': 0.35,    # Swap volume changes
            'liquidity_depth': 0.30,      # Available liquidity
            'concentration_risk': 0.25,    # Whale concentration
            'time_decay': 0.10            # Recency weighting
        }
    
    def calculate_basic_metrics(self, swap_data):
        """Calculate basic risk metrics from swap data"""
        print("\n📊 Calculating Risk Metrics...")
        
        if not swap_data or 'processed_events' not in swap_data:
            print("❌ No swap data found")
            return None
        
        swaps = swap_data['processed_events']
        
        if len(swaps) < 2:
            print("⚠️  Insufficient data for volatility calculation")
            return None
        
        # Extract ETH amounts
        eth_amounts = [s['eth_amount'] for s in swaps]
        
        # Calculate basic metrics
        metrics = {
            'total_volume_eth': sum(eth_amounts),
            'avg_volume_eth': np.mean(eth_amounts),
            'volume_std_eth': np.std(eth_amounts) if len(eth_amounts) > 1 else 0,
            'volume_cv': (np.std(eth_amounts) / np.mean(eth_amounts)) if np.mean(eth_amounts) > 0 else 0,
            'swap_count': len(swaps),
            'time_range_minutes': 5  # Our sample block range
        }
        
        # Calculate volume per minute (liquidity flow)
        metrics['volume_per_minute'] = metrics['total_volume_eth'] / metrics['time_range_minutes']
        
        print(f"   • Total Volume: {metrics['total_volume_eth']:.4f} ETH")
        print(f"   • Average Swap: {metrics['avg_volume_eth']:.4f} ETH")
        print(f"   • Volume Volatility: {metrics['volume_cv']:.3f}")
        print(f"   • Volume/Minute: {metrics['volume_per_minute']:.4f} ETH")
        
        return metrics
    
    def compute_risk_score(self, metrics):
        """Compute a 0-100 risk score from metrics"""
        if not metrics:
            return {"error": "No metrics available"}
        
        print("\n🎯 Computing Risk Score...")
        
        # Normalize metrics to 0-1 scale
        normalized = {}
        
        # Volume volatility (coefficient of variation)
        # Higher volatility = higher risk
        vol_norm = min(metrics['volume_cv'] * 10, 1.0)  # Scale appropriately
        normalized['volatility'] = vol_norm
        
        # Liquidity depth (inverse of volume per minute)
        # Lower liquidity = higher risk
        # Assuming 100 ETH/min is healthy liquidity for our sample
        liquidity_norm = 1 - min(metrics['volume_per_minute'] / 100, 1.0)
        normalized['liquidity'] = liquidity_norm
        
        # Swap concentration (inverse of swap count)
        # Fewer, larger swaps = higher risk
        concentration_norm = 1 - min(metrics['swap_count'] / 10, 1.0)
        normalized['concentration'] = concentration_norm
        
        # Calculate weighted risk score
        risk_score = 0
        risk_score += normalized['volatility'] * self.risk_weights['volume_volatility']
        risk_score += normalized['liquidity'] * self.risk_weights['liquidity_depth']
        risk_score += normalized['concentration'] * self.risk_weights['concentration_risk']
        
        # Scale to 0-100
        final_score = risk_score * 100
        
        # Risk categorization
        if final_score < 30:
            risk_level = "LOW"
            color = "🟢"
        elif final_score < 70:
            risk_level = "MEDIUM"
            color = "🟡"
        else:
            risk_level = "HIGH"
            color = "🔴"
        
        result = {
            'risk_score': round(final_score, 2),
            'risk_level': risk_level,
            'color': color,
            'timestamp': datetime.now().isoformat(),
            'components': {
                'volatility_contrib': round(normalized['volatility'] * self.risk_weights['volume_volatility'] * 100, 2),
                'liquidity_contrib': round(normalized['liquidity'] * self.risk_weights['liquidity_depth'] * 100, 2),
                'concentration_contrib': round(normalized['concentration'] * self.risk_weights['concentration_risk'] * 100, 2)
            },
            'normalized_metrics': {k: round(v, 3) for k, v in normalized.items()}
        }
        
        print(f"   {color} Risk Score: {final_score:.1f}/100 ({risk_level})")
        print(f"   • Volatility contribution: {result['components']['volatility_contrib']:.1f}")
        print(f"   • Liquidity contribution: {result['components']['liquidity_contrib']:.1f}")
        print(f"   • Concentration contribution: {result['components']['concentration_contrib']:.1f}")
        
        return result
    
    def save_risk_assessment(self, metrics, risk_result):
        """Save complete risk assessment"""
        assessment = {
            'metadata': {
                'assessment_time': datetime.now().isoformat(),
                'model_version': 'v0.1-basic',
                'pipeline_phase': '3-ML-Risk-Scoring'
            },
            'metrics': metrics,
            'risk_assessment': risk_result,
            'interpretation': {
                'low_risk': '< 30: Normal market activity',
                'medium_risk': '30-70: Elevated monitoring recommended',
                'high_risk': '> 70: Potential risk event'
            }
        }
        
        with open('risk_assessment.json', 'w') as f:
            json.dump(assessment, f, indent=2)
        
        print(f"\n💾 Risk assessment saved to 'risk_assessment.json'")
        return assessment

def main():
    print("="*60)
    print("DEFI RISK PIPELINE - PHASE 3: RISK SCORING")
    print("="*60)
    
    # Load our captured data
    try:
        with open('structured_swaps.json', 'r') as f:
            swap_data = json.load(f)
        print("✅ Loaded structured swap data")
    except FileNotFoundError:
        print("❌ No swap data found. Run pipeline_fixed.py first.")
        return
    
    # Initialize risk scorer
    scorer = RiskScorer()
    
    # Calculate metrics
    metrics = scorer.calculate_basic_metrics(swap_data)
    
    if metrics:
        # Compute risk score
        risk_result = scorer.compute_risk_score(metrics)
        
        # Save complete assessment
        assessment = scorer.save_risk_assessment(metrics, risk_result)
        
        print("\n✅ PHASE 3 COMPLETE: ML Risk Scoring Foundation")
        print(f"   Next: Deploy as API (Phase 4)")
        
        # Show final result
        print("\n" + "="*60)
        print("FINAL RISK ASSESSMENT")
        print("="*60)
        print(f"Risk Score: {risk_result['color']} {risk_result['risk_score']}/100")
        print(f"Risk Level: {risk_result['risk_level']}")
        print(f"Based on: {metrics['swap_count']} swaps, {metrics['total_volume_eth']:.2f} ETH volume")
        print("="*60)

if __name__ == "__main__":
    main()

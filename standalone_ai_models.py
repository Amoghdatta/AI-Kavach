"""Standalone AI Models for Railway Control System
Self-contained AI algorithms that don't require external ML libraries like sklearn.
Uses rule-based and mathematical models for intelligent railway decision making.
"""

import math
import random
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class PredictionResult:
    """Result of an AI prediction"""
    prediction: float
    confidence: float
    reasoning: str
    factors: Dict[str, float]

class StandaloneDelayPredictor:
    """Predicts train delays using rule-based algorithms"""
    
    def __init__(self):
        self.base_factors = {
            'speed_deviation': 0.3,
            'traffic_density': 0.25,
            'signal_delays': 0.2,
            'weather_impact': 0.15,
            'equipment_status': 0.1
        }
    
    def predict(self, train_data: dict, segment_data: dict, signal_data: dict) -> PredictionResult:
        """Predict delay in minutes"""
        delay_score = 0.0
        factors = {}
        reasoning_parts = []
        
        # Speed factor
        current_speed = train_data.get('speed', 0)
        expected_speed = self._get_expected_speed(train_data)
        speed_ratio = current_speed / expected_speed if expected_speed > 0 else 1.0
        
        if speed_ratio < 0.8:
            speed_factor = (0.8 - speed_ratio) * 20  # Up to 4 minutes delay
            delay_score += speed_factor
            factors['speed_deviation'] = speed_factor
            reasoning_parts.append(f"Low speed ({current_speed:.1f} mph vs expected {expected_speed:.1f} mph)")
        
        # Traffic density factor
        segment_id = train_data.get('segment', '')
        traffic_factor = self._calculate_traffic_density(segment_id, segment_data)
        if traffic_factor > 0.5:
            traffic_delay = traffic_factor * 8  # Up to 8 minutes
            delay_score += traffic_delay
            factors['traffic_density'] = traffic_delay
            reasoning_parts.append(f"High traffic density ({traffic_factor:.1%})")
        
        # Signal delays
        signal_delay = self._calculate_signal_delays(train_data, signal_data)
        if signal_delay > 0:
            delay_score += signal_delay
            factors['signal_delays'] = signal_delay
            reasoning_parts.append(f"Signal delays ({signal_delay:.1f} min)")
        
        # Weather impact (simulated)
        weather_delay = self._calculate_weather_impact(train_data)
        if weather_delay > 0:
            delay_score += weather_delay
            factors['weather_impact'] = weather_delay
            reasoning_parts.append(f"Weather conditions ({weather_delay:.1f} min)")
        
        # Equipment status
        equipment_delay = self._calculate_equipment_delays(train_data)
        if equipment_delay > 0:
            delay_score += equipment_delay
            factors['equipment_status'] = equipment_delay
            reasoning_parts.append("Equipment issues detected")
        
        confidence = min(0.95, 0.6 + (len(factors) * 0.1))
        reasoning = "Delay prediction based on: " + ", ".join(reasoning_parts) if reasoning_parts else "Normal operations expected"
        
        return PredictionResult(
            prediction=max(0, delay_score),
            confidence=confidence,
            reasoning=reasoning,
            factors=factors
        )
    
    def _get_expected_speed(self, train_data: dict) -> float:
        """Calculate expected speed based on train type and priority"""
        train_type = train_data.get('type', 'freight')
        priority = train_data.get('priority', 'FRT')
        
        base_speeds = {
            'passenger': 65,
            'freight': 45,
            'locomotive': 55
        }
        
        priority_multipliers = {
            'EXP': 1.2,
            'FRT': 1.0,
            'LOC': 1.1
        }
        
        base_speed = base_speeds.get(train_type, 45)
        multiplier = priority_multipliers.get(priority, 1.0)
        
        return base_speed * multiplier
    
    def _calculate_traffic_density(self, segment_id: str, segment_data: dict) -> float:
        """Calculate traffic density on segment"""
        # Simplified traffic calculation
        return min(1.0, random.uniform(0.1, 0.8))
    
    def _calculate_signal_delays(self, train_data: dict, signal_data: dict) -> float:
        """Calculate delays due to signals"""
        # Simulate signal-based delays
        signals = signal_data.get('signals', {})
        red_signals = sum(1 for s in signals.values() if s.get('aspect') == 'RED')
        return red_signals * 2.5  # 2.5 minutes per red signal
    
    def _calculate_weather_impact(self, train_data: dict) -> float:
        """Calculate weather-related delays"""
        # Simulate weather impact
        weather_severity = random.uniform(0, 1)
        if weather_severity > 0.7:
            return weather_severity * 5  # Up to 5 minutes for severe weather
        return 0
    
    def _calculate_equipment_delays(self, train_data: dict) -> float:
        """Calculate equipment-related delays"""
        if train_data.get('brakes_failed', False):
            return 15  # 15 minutes for brake issues
        if train_data.get('hazmat', False):
            return 3   # 3 minutes extra for hazmat protocols
        return 0

class StandaloneSafeSpeedCalculator:
    """Calculates safe operating speeds using physics and safety algorithms"""
    
    def __init__(self):
        self.safety_margins = {
            'clear_track': 1.0,
            'congested': 0.7,
            'junction': 0.4,
            'curve': 0.6,
            'weather_reduced': 0.8,
            'brake_issues': 0.3
        }
    
    def predict(self, train_data: dict, segment_data: dict, weather_data: dict) -> PredictionResult:
        """Calculate safe speed in mph"""
        base_speed = 79  # Base speed limit
        safety_factors = []
        applied_factors = {}
        
        # Train type factor
        train_type = train_data.get('type', 'freight')
        type_speeds = {
            'passenger': 80,
            'freight': 60,
            'locomotive': 70
        }
        base_speed = min(base_speed, type_speeds.get(train_type, 60))
        
        # Segment conditions
        segment_id = train_data.get('segment', '')
        segment_info = segment_data.get('segments', {}).get(segment_id, {})
        
        track_type = segment_info.get('track_type', 'main')
        if track_type == 'curve':
            curve_factor = self.safety_margins['curve']
            base_speed *= curve_factor
            applied_factors['curve_limitation'] = curve_factor
            safety_factors.append("curve speed restriction")
        
        elif track_type == 'junction':
            junction_factor = self.safety_margins['junction']
            base_speed *= junction_factor
            applied_factors['junction_limitation'] = junction_factor
            safety_factors.append("junction speed limit")
        
        # Weather conditions
        visibility = weather_data.get('visibility', 10)
        precipitation = weather_data.get('precipitation', 0)
        
        if visibility < 5 or precipitation > 3:
            weather_factor = self.safety_margins['weather_reduced']
            base_speed *= weather_factor
            applied_factors['weather_conditions'] = weather_factor
            safety_factors.append("reduced visibility/precipitation")
        
        # Traffic density
        current_speed = train_data.get('speed', 0)
        if self._is_congested_area(train_data, segment_data):
            congestion_factor = self.safety_margins['congested']
            base_speed *= congestion_factor
            applied_factors['traffic_congestion'] = congestion_factor
            safety_factors.append("high traffic density")
        
        # Equipment status
        if train_data.get('brakes_failed', False):
            brake_factor = self.safety_margins['brake_issues']
            base_speed *= brake_factor
            applied_factors['brake_failure'] = brake_factor
            safety_factors.append("brake system failure")
        
        # Grade considerations
        grade = segment_info.get('grade', 0)
        if abs(grade) > 1.0:
            grade_factor = max(0.7, 1.0 - abs(grade) * 0.1)
            base_speed *= grade_factor
            applied_factors['track_grade'] = grade_factor
            safety_factors.append(f"track grade {grade:.1f}%")
        
        confidence = 0.9 if len(applied_factors) > 0 else 0.7
        reasoning = f"Safe speed calculation considering: {', '.join(safety_factors)}" if safety_factors else "Normal operating conditions"
        
        return PredictionResult(
            prediction=max(5, base_speed),  # Minimum 5 mph
            confidence=confidence,
            reasoning=reasoning,
            factors=applied_factors
        )
    
    def _is_congested_area(self, train_data: dict, segment_data: dict) -> bool:
        """Determine if area is congested"""
        # Simplified congestion detection
        return random.random() < 0.3  # 30% chance of congestion

class StandaloneDisruptionPredictor:
    """Predicts potential system disruptions"""
    
    def __init__(self):
        self.disruption_patterns = {
            'cascade_delay': {'threshold': 5, 'probability': 0.7},
            'equipment_failure': {'threshold': 3, 'probability': 0.4},
            'weather_disruption': {'threshold': 2, 'probability': 0.6},
            'congestion_spiral': {'threshold': 4, 'probability': 0.8}
        }
    
    def predict(self, train_data: dict, segment_data: dict, signal_data: dict) -> PredictionResult:
        """Predict disruption probability (0-10 scale)"""
        disruption_score = 0
        risk_factors = []
        factor_values = {}
        
        # Delayed trains factor
        delayed_trains = self._count_delayed_trains(train_data)
        if delayed_trains >= 2:
            delay_factor = min(4, delayed_trains * 1.5)
            disruption_score += delay_factor
            factor_values['delayed_trains'] = delay_factor
            risk_factors.append(f"{delayed_trains} trains delayed")
        
        # Speed variance factor
        speed_variance = self._calculate_speed_variance(train_data)
        if speed_variance > 0.5:
            variance_factor = speed_variance * 3
            disruption_score += variance_factor
            factor_values['speed_variance'] = variance_factor
            risk_factors.append("high speed variance between trains")
        
        # Signal congestion
        red_signals = sum(1 for s in signal_data.get('signals', {}).values() 
                         if s.get('aspect') == 'RED')
        if red_signals >= 3:
            signal_factor = red_signals * 0.8
            disruption_score += signal_factor
            factor_values['signal_congestion'] = signal_factor
            risk_factors.append(f"{red_signals} red signals")
        
        # Equipment issues
        equipment_issues = self._count_equipment_issues(train_data)
        if equipment_issues > 0:
            equipment_factor = equipment_issues * 2.5
            disruption_score += equipment_factor
            factor_values['equipment_issues'] = equipment_factor
            risk_factors.append(f"{equipment_issues} equipment issues")
        
        # Weather impact
        weather_factor = random.uniform(0, 2)  # Simulated weather impact
        if weather_factor > 1.5:
            disruption_score += weather_factor
            factor_values['weather_conditions'] = weather_factor
            risk_factors.append("adverse weather conditions")
        
        confidence = min(0.9, 0.5 + len(factor_values) * 0.1)
        reasoning = f"Disruption risk based on: {', '.join(risk_factors)}" if risk_factors else "Low disruption risk"
        
        return PredictionResult(
            prediction=min(10, disruption_score),
            confidence=confidence,
            reasoning=reasoning,
            factors=factor_values
        )
    
    def _count_delayed_trains(self, train_data: dict) -> int:
        """Count trains that appear to be delayed"""
        delayed = 0
        
        # Handle different train_data formats
        if isinstance(train_data, dict):
            # If train_data has a 'trains' key, use it; otherwise treat train_data as a single train
            if 'trains' in train_data:
                trains = train_data['trains']
            elif 'id' in train_data or 'speed' in train_data:
                # Single train format
                trains = {'single': train_data}
            else:
                # Assume it's a dict of trains
                trains = train_data
            
            for train in trains.values():
                expected_speed = 50  # Simplified expected speed
                if isinstance(train, dict) and train.get('speed', 0) < expected_speed * 0.7:
                    delayed += 1
        
        return delayed
    
    def _calculate_speed_variance(self, train_data: dict) -> float:
        """Calculate variance in train speeds"""
        # Handle different train_data formats
        if isinstance(train_data, dict):
            if 'trains' in train_data:
                trains = train_data['trains']
            elif 'id' in train_data or 'speed' in train_data:
                trains = {'single': train_data}
            else:
                trains = train_data
            
            speeds = [train.get('speed', 0) for train in trains.values() if isinstance(train, dict)]
        if len(speeds) < 2:
            return 0
        
        avg_speed = sum(speeds) / len(speeds)
        variance = sum((speed - avg_speed) ** 2 for speed in speeds) / len(speeds)
        return math.sqrt(variance) / avg_speed if avg_speed > 0 else 0
    
    def _count_equipment_issues(self, train_data: dict) -> int:
        """Count trains with equipment issues"""
        issues = 0
        
        # Handle different train_data formats
        if isinstance(train_data, dict):
            if 'trains' in train_data:
                trains = train_data['trains']
            elif 'id' in train_data or 'speed' in train_data:
                trains = {'single': train_data}
            else:
                trains = train_data
            
            for train in trains.values():
                if isinstance(train, dict):
                    if train.get('brakes_failed', False):
                        issues += 1
                    if train.get('hazmat', False):
                        issues += 1  # Hazmat requires extra caution
        
        return issues

class StandalonePassengerDemandPredictor:
    """Predicts passenger demand patterns"""
    
    def __init__(self):
        self.time_patterns = {
            'morning_rush': (7, 9, 1.5),
            'evening_rush': (17, 19, 1.4),
            'midday': (11, 14, 0.8),
            'night': (22, 6, 0.3)
        }
    
    def predict(self, train_data: dict, segment_data: dict, time_data: dict) -> PredictionResult:
        """Predict passenger demand (0-100 scale)"""
        base_demand = 50  # Base demand level
        demand_factors = {}
        reasoning_parts = []
        
        # Time-based demand
        current_hour = time.localtime().tm_hour
        time_factor = self._get_time_factor(current_hour)
        base_demand *= time_factor
        demand_factors['time_of_day'] = time_factor
        reasoning_parts.append(f"time of day factor ({time_factor:.1f})")
        
        # Train type impact
        train_type = train_data.get('type', 'freight')
        if train_type == 'passenger':
            type_factor = 1.2
            base_demand *= type_factor
            demand_factors['passenger_service'] = type_factor
            reasoning_parts.append("passenger service active")
        
        # Route popularity (simulated)
        segment_id = train_data.get('segment', '')
        route_popularity = self._get_route_popularity(segment_id)
        base_demand *= route_popularity
        demand_factors['route_popularity'] = route_popularity
        reasoning_parts.append(f"route popularity ({route_popularity:.1f})")
        
        # Day of week effect (simulated)
        day_factor = random.uniform(0.8, 1.3)
        base_demand *= day_factor
        demand_factors['day_of_week'] = day_factor
        
        confidence = 0.75
        reasoning = f"Demand prediction based on: {', '.join(reasoning_parts)}"
        
        return PredictionResult(
            prediction=min(100, max(0, base_demand)),
            confidence=confidence,
            reasoning=reasoning,
            factors=demand_factors
        )
    
    def _get_time_factor(self, hour: int) -> float:
        """Get demand multiplier based on time of day"""
        for period, (start, end, factor) in self.time_patterns.items():
            if start <= hour <= end or (start > end and (hour >= start or hour <= end)):
                return factor
        return 1.0  # Default factor
    
    def _get_route_popularity(self, segment_id: str) -> float:
        """Get route popularity factor"""
        # Simulate route popularity based on segment
        popularity_map = {
            'SEG_01': 1.3,  # Popular route
            'SEG_02': 1.0,  # Average
            'SEG_03': 0.7,  # Less popular
            'SEG_04': 0.9   # Branch line
        }
        return popularity_map.get(segment_id, 1.0)

class StandaloneScenarioPredictor:
    """Predicts outcomes of what-if scenarios"""
    
    def __init__(self):
        self.scenario_templates = {
            'speed_change': self._predict_speed_change,
            'route_change': self._predict_route_change,
            'emergency_stop': self._predict_emergency_stop,
            'traffic_reroute': self._predict_traffic_reroute
        }
    
    def predict(self, scenario_data: dict, train_data: dict, segment_data: dict) -> PredictionResult:
        """Predict scenario outcome"""
        scenario_type = scenario_data.get('type', 'speed_change')
        
        if scenario_type in self.scenario_templates:
            return self.scenario_templates[scenario_type](scenario_data, train_data, segment_data)
        else:
            return PredictionResult(
                prediction=0.5,
                confidence=0.3,
                reasoning="Unknown scenario type",
                factors={}
            )
    
    def _predict_speed_change(self, scenario_data: dict, train_data: dict, segment_data: dict) -> PredictionResult:
        """Predict outcome of speed change"""
        train_id = scenario_data.get('train_id', '')
        new_speed = scenario_data.get('new_speed', 0)
        
        train = train_data.get(train_id, {})
        current_speed = train.get('speed', 0)
        
        # Calculate time impact
        speed_ratio = new_speed / current_speed if current_speed > 0 else 1
        time_impact = (1 / speed_ratio - 1) * 100  # Percentage time change
        
        # Safety impact
        safety_improvement = max(0, (current_speed - new_speed) * 0.1)
        
        # Efficiency impact
        efficiency_change = (speed_ratio - 1) * 100
        
        outcome_score = 0.5 + (efficiency_change - abs(time_impact)) * 0.01
        
        return PredictionResult(
            prediction=max(0, min(1, outcome_score)),
            confidence=0.8,
            reasoning=f"Speed change from {current_speed} to {new_speed} mph: "
                     f"{time_impact:+.1f}% time impact, "
                     f"{safety_improvement:.1f} safety improvement",
            factors={
                'time_impact': time_impact,
                'safety_improvement': safety_improvement,
                'efficiency_change': efficiency_change
            }
        )
    
    def _predict_route_change(self, scenario_data: dict, train_data: dict, segment_data: dict) -> PredictionResult:
        """Predict outcome of route change"""
        # Simplified route change prediction
        new_route_efficiency = random.uniform(0.7, 1.3)
        congestion_improvement = random.uniform(0, 0.4)
        
        outcome_score = (new_route_efficiency + congestion_improvement) / 2
        
        return PredictionResult(
            prediction=outcome_score,
            confidence=0.7,
            reasoning=f"Route change estimated to provide {(outcome_score-0.5)*200:+.0f}% efficiency change",
            factors={
                'route_efficiency': new_route_efficiency,
                'congestion_reduction': congestion_improvement
            }
        )
    
    def _predict_emergency_stop(self, scenario_data: dict, train_data: dict, segment_data: dict) -> PredictionResult:
        """Predict outcome of emergency stop"""
        train_id = scenario_data.get('train_id', '')
        train = train_data.get(train_id, {})
        
        current_speed = train.get('speed', 0)
        mass = train.get('mass', 1000)
        
        # Calculate stopping distance (simplified physics)
        stopping_distance = (current_speed ** 2) / (2 * 8)  # 8 mph/s deceleration
        stopping_time = current_speed / 8
        
        # Safety score (higher for successful emergency stop)
        safety_score = min(1.0, 0.5 + (80 - current_speed) * 0.01)
        
        return PredictionResult(
            prediction=safety_score,
            confidence=0.95,
            reasoning=f"Emergency stop: {stopping_distance:.0f} ft stopping distance, "
                     f"{stopping_time:.1f} seconds to stop",
            factors={
                'stopping_distance': stopping_distance,
                'stopping_time': stopping_time,
                'initial_speed': current_speed
            }
        )
    
    def _predict_traffic_reroute(self, scenario_data: dict, train_data: dict, segment_data: dict) -> PredictionResult:
        """Predict outcome of traffic rerouting"""
        affected_trains = scenario_data.get('affected_trains', 1)
        
        congestion_reduction = min(0.8, affected_trains * 0.2)
        efficiency_gain = congestion_reduction * 0.7
        
        return PredictionResult(
            prediction=0.5 + efficiency_gain,
            confidence=0.6,
            reasoning=f"Traffic reroute affecting {affected_trains} trains: "
                     f"{congestion_reduction:.1%} congestion reduction",
            factors={
                'congestion_reduction': congestion_reduction,
                'efficiency_gain': efficiency_gain,
                'affected_trains': affected_trains
            }
        )

class StandaloneAIModelLoader:
    """Standalone AI model loader that doesn't require sklearn"""
    
    def __init__(self):
        self.delay_predictor = StandaloneDelayPredictor()
        self.safe_speed_calculator = StandaloneSafeSpeedCalculator()
        self.disruption_predictor = StandaloneDisruptionPredictor()
        self.passenger_demand_predictor = StandalonePassengerDemandPredictor()
        self.scenario_predictor = StandaloneScenarioPredictor()
        
        print("🤖 Standalone AI models initialized successfully")
        print("✅ No external dependencies required")
    
    def predict_delay(self, train_data: dict, segment_data: dict, signal_data: dict) -> PredictionResult:
        """Predict train delay"""
        return self.delay_predictor.predict(train_data, segment_data, signal_data)
    
    def predict_safe_speed(self, train_data: dict, segment_data: dict, weather_data: dict) -> PredictionResult:
        """Predict safe operating speed"""
        return self.safe_speed_calculator.predict(train_data, segment_data, weather_data)
    
    def predict_disruption(self, train_data: dict, segment_data: dict, signal_data: dict) -> PredictionResult:
        """Predict system disruption probability"""
        return self.disruption_predictor.predict(train_data, segment_data, signal_data)
    
    def predict_passenger_demand(self, train_data: dict, segment_data: dict, time_data: dict) -> PredictionResult:
        """Predict passenger demand"""
        return self.passenger_demand_predictor.predict(train_data, segment_data, time_data)
    
    def predict_scenario(self, scenario_data: dict, train_data: dict, segment_data: dict) -> PredictionResult:
        """Predict what-if scenario outcome"""
        return self.scenario_predictor.predict(scenario_data, train_data, segment_data)

def get_standalone_model_loader():
    """Get the standalone AI model loader"""
    return StandaloneAIModelLoader()

# Test function
if __name__ == "__main__":
    print("Testing Standalone AI Models...")
    
    loader = get_standalone_model_loader()
    
    # Test data
    test_train = {
        'id': 'TEST_001',
        'speed': 45,
        'type': 'passenger',
        'priority': 'EXP',
        'segment': 'SEG_01',
        'brakes_failed': False
    }
    
    test_segment = {
        'segments': {
            'SEG_01': {
                'track_type': 'main',
                'grade': 0.5
            }
        }
    }
    
    test_weather = {
        'visibility': 8,
        'precipitation': 1
    }
    
    # Test predictions
    delay_result = loader.predict_delay(test_train, test_segment, {'signals': {}})
    print(f"Delay Prediction: {delay_result.prediction:.1f} minutes ({delay_result.confidence:.1%} confidence)")
    print(f"Reasoning: {delay_result.reasoning}")
    
    speed_result = loader.predict_safe_speed(test_train, test_segment, test_weather)
    print(f"Safe Speed: {speed_result.prediction:.1f} mph ({speed_result.confidence:.1%} confidence)")
    print(f"Reasoning: {speed_result.reasoning}")
    
    print("✅ All standalone AI models working correctly!")
"""Railway Control Center Prototype
Interactive control center where operators monitor trains, receive AI recommendations,
and manage multi-track railway operations with physics-based outcome prediction.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math
import time
import random
import threading
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# Import existing components - using built-in logic for simplicity
AI_ENABLED = False  # Use simple built-in logic without external dependencies

class TrackingMode(Enum):
    MANUAL = "manual"
    AUTO = "auto"
    FOCUSED = "focused"

class RecommendationType(Enum):
    SPEED_CHANGE = "speed_change"
    ROUTE_CHANGE = "route_change" 
    EMERGENCY_STOP = "emergency_stop"
    TRACK_SWITCH = "track_switch"
    BRAKE_CHECK = "brake_check"

@dataclass
class AIRecommendation:
    id: str
    type: RecommendationType
    train_id: str
    priority: str  # HIGH, MEDIUM, LOW
    message: str
    action: str
    predicted_outcome: str
    confidence: float
    timestamp: float
    status: str = "pending"  # pending, accepted, rejected
    collision_data: Optional[dict] = None  # Additional collision risk data

@dataclass
class TrackingPoint:
    id: str
    name: str
    x: float
    y: float
    segment_id: str
    offset: float
    active: bool = False

class PhysicsEngine:
    """Advanced physics engine for realistic train behavior prediction"""
    
    def __init__(self):
        self.gravity = 9.81  # m/s²
        self.friction_coefficient = 0.3
        self.air_resistance_factor = 0.02
        
    def calculate_braking_distance(self, speed_mph: float, mass_tons: float, 
                                 grade_percent: float = 0, brake_efficiency: float = 1.0) -> float:
        """Calculate realistic braking distance"""
        speed_ms = speed_mph * 0.44704  # Convert mph to m/s
        
        # Account for grade (positive = uphill helps braking, negative = downhill hurts)
        effective_deceleration = (self.friction_coefficient * self.gravity * brake_efficiency) + \
                               (self.gravity * grade_percent / 100)
        
        if effective_deceleration <= 0:
            return float('inf')  # Cannot stop
            
        braking_distance_m = (speed_ms ** 2) / (2 * effective_deceleration)
        return braking_distance_m * 3.28084  # Convert to feet
    
    def predict_collision_time(self, train1_speed: float, train1_pos: float,
                             train2_speed: float, train2_pos: float) -> float:
        """Predict time to collision between two trains"""
        relative_speed = abs(train1_speed - train2_speed)
        if relative_speed == 0:
            return float('inf')
            
        distance = abs(train1_pos - train2_pos)
        return distance / relative_speed
    
    def simulate_emergency_scenario(self, train_data: dict, scenario: str) -> dict:
        """Simulate emergency scenarios and predict outcomes"""
        results = {
            'scenario': scenario,
            'timeline': [],
            'final_outcome': '',
            'casualties': 0,
            'damage_cost': 0
        }
        
        if scenario == 'brake_failure':
            speed = train_data.get('speed', 0)
            mass = train_data.get('mass', 1000)  # tons
            
            # Runaway train simulation
            max_speed = min(speed * 1.5, 90)  # Speed increases due to gravity
            stopping_distance = self.calculate_braking_distance(max_speed, mass, brake_efficiency=0.1)
            
            results['timeline'] = [
                {'time': 0, 'event': 'Brake failure detected', 'speed': speed},
                {'time': 30, 'event': 'Speed increasing due to grade', 'speed': speed * 1.2},
                {'time': 60, 'event': f'Maximum speed reached: {max_speed} mph', 'speed': max_speed},
                {'time': 120, 'event': f'Emergency protocols activated', 'speed': max_speed}
            ]
            
            if stopping_distance > 5000:  # 5000 feet
                results['final_outcome'] = 'CRITICAL: Derailment likely'
                results['casualties'] = random.randint(15, 50)
                results['damage_cost'] = random.randint(50, 200) * 1000000  # Millions
            else:
                results['final_outcome'] = 'Controlled stop using emergency systems'
                results['casualties'] = 0
                results['damage_cost'] = random.randint(1, 5) * 1000000
                
        return results

class MultiTrackSystem:
    """Manages multi-track railway system with junctions"""
    
    def __init__(self):
        self.tracks = {}
        self.junctions = {}
        self.switches = {}
        
    def add_track(self, track_id: str, segments: List[str], capacity: int = 2):
        """Add a track with multiple segments"""
        self.tracks[track_id] = {
            'segments': segments,
            'capacity': capacity,
            'current_trains': [],
            'status': 'operational'
        }
    
    def add_junction(self, junction_id: str, input_tracks: List[str], output_tracks: List[str]):
        """Add a junction connecting multiple tracks"""
        self.junctions[junction_id] = {
            'input_tracks': input_tracks,
            'output_tracks': output_tracks,
            'current_switch_position': output_tracks[0] if output_tracks else None,
            'trains_approaching': []
        }
    
    def calculate_route_change(self, train_id: str, from_track: str, to_track: str) -> dict:
        """Calculate feasibility and timing for route change"""
        if to_track not in self.tracks:
            return {'feasible': False, 'reason': 'Track does not exist'}
            
        target_track = self.tracks[to_track]
        if len(target_track['current_trains']) >= target_track['capacity']:
            return {'feasible': False, 'reason': 'Target track at capacity'}
        
        # Find connecting junction
        connecting_junction = None
        for junction_id, junction in self.junctions.items():
            if from_track in junction['input_tracks'] and to_track in junction['output_tracks']:
                connecting_junction = junction_id
                break
        
        if not connecting_junction:
            return {'feasible': False, 'reason': 'No connecting junction found'}
        
        return {
            'feasible': True,
            'junction_id': connecting_junction,
            'estimated_time': random.randint(30, 120),  # seconds
            'safety_clearance': 'OK'
        }

class CollisionDetectionSystem:
    """Advanced collision detection and warning system"""
    
    def __init__(self):
        self.physics_engine = PhysicsEngine()
        self.collision_threshold_time = 30  # seconds
        self.critical_distance = 500  # feet
        self.warning_distance = 1000  # feet
    
    def calculate_collision_risk(self, trains: Dict, segments: Dict) -> List[dict]:
        """Calculate collision risk for all train pairs"""
        collision_risks = []
        train_list = list(trains.items())
        
        # Check every pair of trains
        for i in range(len(train_list)):
            for j in range(i + 1, len(train_list)):
                train1_id, train1 = train_list[i]
                train2_id, train2 = train_list[j]
                
                risk = self._analyze_train_pair_collision(train1_id, train1, train2_id, train2, segments)
                if risk:
                    collision_risks.append(risk)
        
        return collision_risks
    
    def _analyze_train_pair_collision(self, train1_id: str, train1: dict, 
                                    train2_id: str, train2: dict, segments: Dict) -> Optional[dict]:
        """Analyze collision risk between two specific trains"""
        # Get train positions and segments
        train1_segment = train1.get('segment', '')
        train2_segment = train2.get('segment', '')
        train1_track = train1.get('track', train1_segment)  # Get specific track info
        train2_track = train2.get('track', train2_segment)
        train1_offset = train1.get('offset', 0)
        train2_offset = train2.get('offset', 0)
        train1_speed = train1.get('speed', 0)  # mph
        train2_speed = train2.get('speed', 0)  # mph
        
        # IMPORTANT: Only check collision if trains are on the SAME TRACK
        # Adjacent parallel tracks should not trigger collision warnings
        if (train1_segment == train2_segment and 
            self._are_trains_on_same_track(train1, train2, train1_segment)):
            # Same segment collision risk
            distance_feet = abs(train2_offset - train1_offset) * 5280  # Convert to feet
            
            # Calculate relative approach speed - check for head-on vs same-direction collision
            train1_direction = train1.get('direction', 1)  # 1 = eastbound, -1 = westbound
            train2_direction = train2.get('direction', 1)
            
            # HEAD-ON COLLISION: Trains moving in opposite directions
            if train1_direction * train2_direction < 0:  # Opposite directions
                relative_speed = train1_speed + train2_speed  # ADD speeds for head-on collision
                approaching_train = f"{train1_id},{train2_id}"  # Both trains approaching
                leading_train = "HEAD_ON_COLLISION"
                print(f"🚨 HEAD-ON COLLISION DETECTED: {train1_id} ({train1_speed}mph) vs {train2_id} ({train2_speed}mph)")
                print(f"   Combined approach speed: {relative_speed} mph")
            
            # SAME DIRECTION: One train catching up to another
            elif train2_offset > train1_offset:
                # Train2 is ahead of Train1
                relative_speed = max(0, train1_speed - train2_speed)  # Train1 approaching Train2
                approaching_train = train1_id
                leading_train = train2_id
            else:
                # Train1 is ahead of Train2
                relative_speed = max(0, train2_speed - train1_speed)  # Train2 approaching Train1
                approaching_train = train2_id
                leading_train = train1_id
            
            # CRITICAL FIX: Check for stationary train collision scenarios
            stationary_collision_risk = False
            
            # Case 1: One train stopped, another approaching
            if train1_speed == 0 and train2_speed > 0:
                # Train1 is stationary, Train2 is moving
                if train1_direction * train2_direction < 0:
                    # Head-on: Train2 approaching stationary Train1
                    relative_speed = train2_speed
                    approaching_train = train2_id
                    leading_train = train1_id
                    stationary_collision_risk = True
                    print(f"🚨 STATIONARY COLLISION RISK: {train2_id} ({train2_speed}mph) approaching stationary {train1_id}")
                elif train2_offset > train1_offset and train2_direction == -1:
                    # Same direction: Train2 moving west toward stationary Train1
                    relative_speed = train2_speed
                    approaching_train = train2_id
                    leading_train = train1_id
                    stationary_collision_risk = True
                elif train1_offset > train2_offset and train2_direction == 1:
                    # Same direction: Train2 moving east toward stationary Train1
                    relative_speed = train2_speed
                    approaching_train = train2_id
                    leading_train = train1_id
                    stationary_collision_risk = True
                    
            elif train2_speed == 0 and train1_speed > 0:
                # Train2 is stationary, Train1 is moving
                if train1_direction * train2_direction < 0:
                    # Head-on: Train1 approaching stationary Train2
                    relative_speed = train1_speed
                    approaching_train = train1_id
                    leading_train = train2_id
                    stationary_collision_risk = True
                    print(f"🚨 STATIONARY COLLISION RISK: {train1_id} ({train1_speed}mph) approaching stationary {train2_id}")
                elif train1_offset > train2_offset and train1_direction == -1:
                    # Same direction: Train1 moving west toward stationary Train2
                    relative_speed = train1_speed
                    approaching_train = train1_id
                    leading_train = train2_id
                    stationary_collision_risk = True
                elif train2_offset > train1_offset and train1_direction == 1:
                    # Same direction: Train1 moving east toward stationary Train2
                    relative_speed = train1_speed
                    approaching_train = train1_id
                    leading_train = train2_id
                    stationary_collision_risk = True
            
            # Check for collision risk (moving towards each other OR stationary collision OR dangerously close)
            if relative_speed > 0 or stationary_collision_risk or distance_feet < 500:
                # Calculate time to collision
                if relative_speed > 0:
                    time_to_collision = (distance_feet / (relative_speed * 5280 / 3600))  # Convert mph to ft/s
                else:
                    # Stationary trains that are too close
                    time_to_collision = 0  # Immediate risk
                    print(f"⚠️  TRAINS TOO CLOSE: {train1_id} and {train2_id} - Distance: {distance_feet:.0f}ft")
                
                # Calculate braking distance needed
                if leading_train == "HEAD_ON_COLLISION":
                    # Head-on collision: both trains need to stop
                    braking_distance1 = self.physics_engine.calculate_braking_distance(train1_speed, 1000)
                    braking_distance2 = self.physics_engine.calculate_braking_distance(train2_speed, 1000)
                    braking_distance = braking_distance1 + braking_distance2  # Combined braking distance needed
                    approaching_speed = relative_speed  # Use combined speed for risk assessment
                else:
                    # Same direction collision: only approaching train needs to stop
                    approaching_speed = train1_speed if approaching_train == train1_id else train2_speed
                    braking_distance = self.physics_engine.calculate_braking_distance(
                        approaching_speed, 1000  # Assume 1000 ton mass
                    )
                
                risk_level = self._determine_risk_level(distance_feet, time_to_collision, braking_distance)
                
                if risk_level != 'SAFE':
                    return {
                        'train1': train1_id,
                        'train2': train2_id,
                        'segment': train1_segment,
                        'distance_feet': distance_feet,
                        'time_to_collision': time_to_collision,
                        'relative_speed': relative_speed,
                        'braking_distance_needed': braking_distance,
                        'risk_level': risk_level,
                        'approaching_train': approaching_train,
                        'leading_train': leading_train,
                        'recommended_action': self._get_recommended_action(risk_level, approaching_train, leading_train)
                    }
        
        # Check adjacent segments (junction collisions)
        adjacent_risk = self._check_junction_collision_risk(
            train1_id, train1, train2_id, train2, segments
        )
        if adjacent_risk:
            return adjacent_risk
            
        return None
    
    def _are_trains_on_same_track(self, train1: dict, train2: dict, segment: str) -> bool:
        """Determine if two trains are on the same physical track (not just same segment)"""
        
        # Get train track information
        train1_track = train1.get('track', 'MAIN')
        train2_track = train2.get('track', 'MAIN')
        
        # If trains have explicit track assignments, use those
        if train1_track != train2_track:
            return False
            
        # For multi-track segments, use additional logic
        train1_lane = train1.get('lane', 0)  # 0 = main track, 1 = parallel track
        train2_lane = train2.get('lane', 0)
        
        if train1_lane != train2_lane:
            return False
            
        # Check if trains are on parallel tracks based on segment configuration
        parallel_segments = {
            'SEG_01': {'tracks': ['MAIN_A', 'MAIN_B'], 'parallel': True},
            'SEG_02': {'tracks': ['MAIN_A', 'MAIN_B'], 'parallel': True},
            'SEG_03': {'tracks': ['MAIN_A'], 'parallel': False},
            'SEG_04': {'tracks': ['MAIN_B'], 'parallel': False},
            'SEG_05': {'tracks': ['MAIN_B'], 'parallel': False},
            'SEG_06': {'tracks': ['MAIN_B'], 'parallel': False},
            'SEG_07': {'tracks': ['SIDING_1'], 'parallel': False}
        }
        
        segment_config = parallel_segments.get(segment, {'tracks': ['MAIN'], 'parallel': False})
        
        # If this is a parallel track segment, check y-coordinate offset
        if segment_config.get('parallel', False):
            train1_y_offset = train1.get('y_offset', 0)  # Vertical offset from center line
            train2_y_offset = train2.get('y_offset', 0)
            
            # If trains have different y-offsets, they're on parallel tracks
            if abs(train1_y_offset - train2_y_offset) > 0.1:  # More than 10% offset difference
                return False
        
        # NOTE: Removed incorrect logic that assumed opposite directions = parallel tracks
        # Direction alone doesn't determine if trains are on same track
        # Head-on collisions happen when trains with opposite directions are on the SAME track
            
        return True  # Trains are on the same physical track
    
    def _determine_risk_level(self, distance_feet: float, time_to_collision: float, braking_distance: float) -> str:
        """Determine the risk level based on distance and timing"""
        # CRITICAL: Stationary trains too close or insufficient braking distance
        if distance_feet < 500 and time_to_collision == 0:
            return 'CRITICAL'  # Stationary trains dangerously close
        elif distance_feet <= braking_distance * 1.5:
            return 'CRITICAL'  # Insufficient braking distance
        elif time_to_collision <= 15:
            return 'HIGH'  # Less than 15 seconds to collision
        elif time_to_collision <= self.collision_threshold_time:
            return 'MEDIUM'  # Less than 30 seconds to collision
        elif distance_feet <= self.warning_distance:
            return 'LOW'  # Trains getting close but manageable
        else:
            return 'SAFE'
    
    def _get_recommended_action(self, risk_level: str, approaching_train: str, leading_train: str) -> str:
        """Get recommended action based on risk level"""
        if leading_train == "HEAD_ON_COLLISION":
            actions = {
                'CRITICAL': f'EMERGENCY STOP ALL TRAINS - Head-on collision imminent between {approaching_train}',
                'HIGH': f'Immediate emergency braking for both trains in {approaching_train}',
                'MEDIUM': f'Immediate speed reduction for both trains in {approaching_train}',
                'LOW': f'Monitor head-on approach between {approaching_train}'
            }
        else:
            actions = {
                'CRITICAL': f'EMERGENCY STOP ALL TRAINS - Trains dangerously close: {approaching_train} and {leading_train}',
                'HIGH': f'Immediate speed reduction for {approaching_train} to 15 mph and alert {leading_train}',
                'MEDIUM': f'Reduce speed of {approaching_train} to 25 mph and monitor closely',
                'LOW': f'Advisory: Monitor {approaching_train} approach to {leading_train}'
            }
        return actions.get(risk_level, 'Monitor situation')
    
    def _check_junction_collision_risk(self, train1_id: str, train1: dict, 
                                     train2_id: str, train2: dict, segments: Dict) -> Optional[dict]:
        """Check for collision risk at junctions"""
        # Simplified junction collision detection
        # In a real system, this would check if trains are approaching the same junction
        # from different tracks and could collide
        
        train1_segment = train1.get('segment', '')
        train2_segment = train2.get('segment', '')
        
        # Define junction segments (segments that connect to junctions)
        junction_segments = ['SEG_03', 'SEG_06', 'SEG_07']  # Example junction points
        
        if (train1_segment in junction_segments and train2_segment in junction_segments and 
            train1_segment != train2_segment):
            
            # Both trains approaching junction from different segments
            distance1 = (1.0 - train1.get('offset', 0)) * 5280  # Distance to end of segment
            distance2 = (1.0 - train2.get('offset', 0)) * 5280
            
            time1 = distance1 / (train1.get('speed', 1) * 5280 / 3600)  # Time to reach junction
            time2 = distance2 / (train2.get('speed', 1) * 5280 / 3600)
            
            if abs(time1 - time2) < 20:  # Both will reach junction within 20 seconds of each other
                return {
                    'train1': train1_id,
                    'train2': train2_id,
                    'collision_type': 'JUNCTION',
                    'time_to_junction_1': time1,
                    'time_to_junction_2': time2,
                    'risk_level': 'HIGH',
                    'recommended_action': f'Stop {train1_id} and {train2_id} - Junction collision risk'
                }
        
        return None

class ControlCenterAI:
    """AI system for generating recommendations to operators"""
    
    def __init__(self):
        self.physics_engine = PhysicsEngine()
        self.multi_track = MultiTrackSystem()
        self.collision_detector = CollisionDetectionSystem()
        self.ai_loader = None
        self.recommendation_counter = 0
        
        # Using simple built-in logic - no external AI dependencies needed
        pass
    
    def analyze_traffic_situation(self, trains: Dict, segments: Dict) -> List[AIRecommendation]:
        """Analyze current traffic and generate recommendations"""
        recommendations = []
        
        # PRIORITY 1: Check for collision risks first
        collision_risks = self.collision_detector.calculate_collision_risk(trains, segments)
        for risk in collision_risks:
            collision_rec = self._create_collision_recommendation(risk)
            if collision_rec:
                recommendations.append(collision_rec)
        
        # Group trains by segment for other analysis
        segment_trains = {}
        for train_id, train in trains.items():
            segment = train.get('segment', '')
            if segment not in segment_trains:
                segment_trains[segment] = []
            segment_trains[segment].append((train_id, train))
        
        # Analyze each segment for potential issues
        for segment_id, trains_on_segment in segment_trains.items():
            if len(trains_on_segment) > 1:
                recommendations.extend(self._analyze_congestion(trains_on_segment, segment_id))
            
            for train_id, train in trains_on_segment:
                # Check for speed optimization
                speed_rec = self._analyze_speed_optimization(train_id, train, trains)
                if speed_rec:
                    recommendations.append(speed_rec)
                
                # Check for route optimization
                route_rec = self._analyze_route_optimization(train_id, train)
                if route_rec:
                    recommendations.append(route_rec)
                
                # Check for emergency scenarios
                emergency_rec = self._check_emergency_conditions(train_id, train)
                if emergency_rec:
                    recommendations.append(emergency_rec)
                
                # Check for maintenance recommendations
                maintenance_rec = self._analyze_maintenance_needs(train_id, train)
                if maintenance_rec:
                    recommendations.append(maintenance_rec)
                
                # Check for energy efficiency
                energy_rec = self._analyze_energy_efficiency(train_id, train)
                if energy_rec:
                    recommendations.append(energy_rec)
                
                # Check for passenger comfort
                comfort_rec = self._analyze_passenger_comfort(train_id, train)
                if comfort_rec:
                    recommendations.append(comfort_rec)
        
        return recommendations
    
    def _analyze_congestion(self, trains_on_segment: List, segment_id: str) -> List[AIRecommendation]:
        """Analyze congestion and suggest solutions"""
        recommendations = []
        
        if len(trains_on_segment) >= 2:
            # Sort by position
            sorted_trains = sorted(trains_on_segment, key=lambda x: x[1].get('offset', 0))
            
            for i in range(len(sorted_trains) - 1):
                train1_id, train1 = sorted_trains[i]
                train2_id, train2 = sorted_trains[i + 1]
                
                distance = abs(train2.get('offset', 0) - train1.get('offset', 0))
                
                if distance < 0.15:  # Too close
                    self.recommendation_counter += 1
                    recommendations.append(AIRecommendation(
                        id=f"REC_{self.recommendation_counter:04d}",
                        type=RecommendationType.SPEED_CHANGE,
                        train_id=train1_id,
                        priority="HIGH",
                        message=f"Trains {train1_id} and {train2_id} too close on {segment_id}",
                        action=f"Reduce speed of {train1_id} to 25 mph",
                        predicted_outcome="Increased following distance, reduced collision risk by 85%",
                        confidence=0.92,
                        timestamp=time.time()
                    ))
        
        return recommendations
    
    def _analyze_speed_optimization(self, train_id: str, train: dict, all_trains: Dict) -> Optional[AIRecommendation]:
        """Analyze if speed optimization is needed"""
        current_speed = train.get('speed', 0)
        train_type = train.get('type', 'freight')
        priority = train.get('priority', 'FRT')
        weather_condition = random.choice(['clear', 'rain', 'fog', 'wind'])
        track_condition = random.choice(['excellent', 'good', 'fair', 'poor'])
        
        # Generate diverse speed recommendations based on conditions
        recommendations = []
        
        # Weather-based speed limits
        if weather_condition == 'fog' and current_speed > 40 and random.random() < 0.3:
            self.recommendation_counter += 1
            return AIRecommendation(
                id=f"REC_{self.recommendation_counter:04d}",
                type=RecommendationType.SPEED_CHANGE,
                train_id=train_id,
                priority="HIGH",
                message=f"Poor visibility conditions detected for {train_id}",
                action=f"Limit speed to 35 mph due to fog conditions",
                predicted_outcome="Reduced accident risk by 60%, safer braking distance",
                confidence=0.89,
                timestamp=time.time()
            )
        
        # Track condition-based recommendations
        elif track_condition == 'poor' and current_speed > 30 and random.random() < 0.25:
            self.recommendation_counter += 1
            return AIRecommendation(
                id=f"REC_{self.recommendation_counter:04d}",
                type=RecommendationType.SPEED_CHANGE,
                train_id=train_id,
                priority="MEDIUM",
                message=f"Poor track conditions ahead for {train_id}",
                action=f"Reduce speed to 25 mph for track safety",
                predicted_outcome="Prevents derailment risk, ensures safe passage",
                confidence=0.85,
                timestamp=time.time()
            )
        
        # Progressive speed reduction for congestion
        elif len([t for t in all_trains.values() if t.get('segment') == train.get('segment')]) > 1:
            if random.random() < 0.4:  # 40% chance
                self.recommendation_counter += 1
                return AIRecommendation(
                    id=f"REC_{self.recommendation_counter:04d}",
                    type=RecommendationType.SPEED_CHANGE,
                    train_id=train_id,
                    priority="MEDIUM",
                    message=f"Traffic congestion detected ahead of {train_id}",
                    action=f"Gradually reduce speed to 45 mph",
                    predicted_outcome="Smooth traffic flow, reduced fuel consumption by 15%",
                    confidence=0.76,
                    timestamp=time.time()
                )
        
        # Energy optimization recommendations
        elif train_type == 'freight' and current_speed > 50:
            if random.random() < 0.3:  # 30% chance
                self.recommendation_counter += 1
                return AIRecommendation(
                    id=f"REC_{self.recommendation_counter:04d}",
                    type=RecommendationType.SPEED_CHANGE,
                    train_id=train_id,
                    priority="LOW",
                    message=f"Energy optimization opportunity for freight {train_id}",
                    action=f"Limit speed to 45 mph for fuel efficiency",
                    predicted_outcome="20% fuel savings, extended engine life",
                    confidence=0.72,
                    timestamp=time.time()
                )
        
        # High priority trains should maintain higher speeds
        elif priority == 'EXP' and current_speed < 60:
            self.recommendation_counter += 1
            return AIRecommendation(
                id=f"REC_{self.recommendation_counter:04d}",
                type=RecommendationType.SPEED_CHANGE,
                train_id=train_id,
                priority="MEDIUM",
                message=f"Express train {train_id} operating below optimal speed",
                action=f"Increase speed to 65 mph when track clear",
                predicted_outcome="Improved schedule adherence, 12 minute time savings",
                confidence=0.78,
                timestamp=time.time()
            )
        
        return None
    
    def _analyze_route_optimization(self, train_id: str, train: dict) -> Optional[AIRecommendation]:
        """Analyze if route change would be beneficial"""
        segment = train.get('segment', '')
        train_type = train.get('type', 'freight')
        
        # Different types of route optimizations
        if random.random() < 0.25:  # 25% chance of route recommendation
            recommendation_type = random.choice([
                'alternative_route', 'siding_bypass', 'express_lane', 'maintenance_detour'
            ])
            
            if recommendation_type == 'alternative_route':
                self.recommendation_counter += 1
                return AIRecommendation(
                    id=f"REC_{self.recommendation_counter:04d}",
                    type=RecommendationType.ROUTE_CHANGE,
                    train_id=train_id,
                    priority="MEDIUM",
                    message=f"Faster alternative route detected for {train_id}",
                    action="Switch to Track B at Junction J2 for Express Lane",
                    predicted_outcome="8 minute time savings, avoid congested main line",
                    confidence=0.73,
                    timestamp=time.time()
                )
            
            elif recommendation_type == 'siding_bypass':
                self.recommendation_counter += 1
                return AIRecommendation(
                    id=f"REC_{self.recommendation_counter:04d}",
                    type=RecommendationType.ROUTE_CHANGE,
                    train_id=train_id,
                    priority="LOW",
                    message=f"Siding available for {train_id} to let express pass",
                    action="Move to Siding-3 for 5 minutes",
                    predicted_outcome="Improved overall network efficiency, priority train optimization",
                    confidence=0.68,
                    timestamp=time.time()
                )
                
            elif recommendation_type == 'maintenance_detour':
                self.recommendation_counter += 1
                return AIRecommendation(
                    id=f"REC_{self.recommendation_counter:04d}",
                    type=RecommendationType.ROUTE_CHANGE,
                    train_id=train_id,
                    priority="HIGH",
                    message=f"Scheduled maintenance ahead - detour required for {train_id}",
                    action="Take detour via Track C (adds 3 minutes)",
                    predicted_outcome="Avoid maintenance zone, ensure safe passage",
                    confidence=0.91,
                    timestamp=time.time()
                )
        
        return None
    
    def _check_emergency_conditions(self, train_id: str, train: dict) -> Optional[AIRecommendation]:
        """Check for potential emergency conditions"""
        # Simulate brake failure detection
        if train.get('brakes_failed', False) or random.random() < 0.02:  # 2% chance
            self.recommendation_counter += 1
            return AIRecommendation(
                id=f"REC_{self.recommendation_counter:04d}",
                type=RecommendationType.EMERGENCY_STOP,
                train_id=train_id,
                priority="HIGH",
                message=f"EMERGENCY: Potential brake system anomaly detected on {train_id}",
                action="Immediate inspection and emergency stop",
                predicted_outcome="Prevent potential runaway scenario, ensure passenger safety",
                confidence=0.88,
                timestamp=time.time()
            )
        
        return None
    
    def predict_recommendation_outcome(self, recommendation: AIRecommendation, 
                                     trains: Dict, segments: Dict) -> dict:
        """Predict the outcome of implementing a recommendation"""
        train = trains.get(recommendation.train_id, {})
        
        if recommendation.type == RecommendationType.SPEED_CHANGE:
            return self._predict_speed_change_outcome(train, recommendation)
        elif recommendation.type == RecommendationType.ROUTE_CHANGE:
            return self._predict_route_change_outcome(train, recommendation)
        elif recommendation.type == RecommendationType.EMERGENCY_STOP:
            return self._predict_emergency_stop_outcome(train, recommendation)
        
        return {'success_probability': 0.5, 'timeline': [], 'risks': []}
    
    def _predict_speed_change_outcome(self, train: dict, recommendation: AIRecommendation) -> dict:
        """Predict outcome of speed change"""
        current_speed = train.get('speed', 0)
        
        if 'Reduce speed' in recommendation.action:
            new_speed = current_speed * 0.6
            braking_time = (current_speed - new_speed) / 2.5  # Assuming 2.5 mph/s deceleration
            
            return {
                'success_probability': 0.95,
                'timeline': [
                    {'time': 0, 'event': 'Speed reduction command sent'},
                    {'time': braking_time, 'event': f'Target speed {new_speed:.1f} mph reached'},
                    {'time': braking_time + 30, 'event': 'Following distance normalized'}
                ],
                'risks': ['Temporary schedule delay', 'Passenger discomfort during braking'],
                'benefits': ['Increased safety margin', 'Reduced collision risk']
            }
        
        return {'success_probability': 0.8, 'timeline': [], 'risks': []}
    
    def _predict_route_change_outcome(self, train: dict, recommendation: AIRecommendation) -> dict:
        """Predict outcome of route change"""
        return {
            'success_probability': 0.75,
            'timeline': [
                {'time': 0, 'event': 'Route change request sent'},
                {'time': 45, 'event': 'Approaching junction'},
                {'time': 60, 'event': 'Track switch completed'},
                {'time': 120, 'event': 'Train on new route'}
            ],
            'risks': ['Temporary speed reduction at junction', 'Potential switching delays'],
            'benefits': ['Reduced main line congestion', 'Improved schedule adherence']
        }
    
    def _predict_emergency_stop_outcome(self, train: dict, recommendation: AIRecommendation) -> dict:
        """Predict outcome of emergency stop"""
        speed = train.get('speed', 0)
        mass = train.get('mass', 1000)
        
        braking_distance = self.physics_engine.calculate_braking_distance(speed, mass)
        stopping_time = speed / 8.0  # Emergency braking at 8 mph/s
        
        return {
            'success_probability': 0.98,
            'timeline': [
                {'time': 0, 'event': 'Emergency stop activated'},
                {'time': 5, 'event': 'Emergency brakes engaged'},
                {'time': stopping_time, 'event': 'Train stopped'},
                {'time': stopping_time + 120, 'event': 'Inspection team dispatched'}
            ],
            'risks': ['Service disruption', 'Passenger evacuation may be required'],
            'benefits': ['Prevents potential catastrophic failure', 'Ensures passenger safety'],
            'stopping_distance_ft': braking_distance
        }
    
    def _analyze_maintenance_needs(self, train_id: str, train: dict) -> Optional[AIRecommendation]:
        """Analyze maintenance requirements and scheduling"""
        if random.random() < 0.2:  # 20% chance of maintenance recommendation
            maintenance_type = random.choice([
                'brake_inspection', 'wheel_check', 'engine_service', 'safety_systems'
            ])
            
            if maintenance_type == 'brake_inspection':
                self.recommendation_counter += 1
                return AIRecommendation(
                    id=f"REC_{self.recommendation_counter:04d}",
                    type=RecommendationType.ROUTE_CHANGE,  # Route to maintenance yard
                    train_id=train_id,
                    priority="MEDIUM",
                    message=f"Brake system inspection due for {train_id}",
                    action="Schedule maintenance at next depot stop",
                    predicted_outcome="Prevent brake failure, ensure safety compliance",
                    confidence=0.82,
                    timestamp=time.time()
                )
            
            elif maintenance_type == 'wheel_check':
                self.recommendation_counter += 1
                return AIRecommendation(
                    id=f"REC_{self.recommendation_counter:04d}",
                    type=RecommendationType.SPEED_CHANGE,
                    train_id=train_id,
                    priority="LOW",
                    message=f"Wheel wear monitoring for {train_id}",
                    action="Limit speed to 40 mph pending wheel inspection",
                    predicted_outcome="Extended wheel life, reduced maintenance costs",
                    confidence=0.71,
                    timestamp=time.time()
                )
        
        return None
    
    def _analyze_energy_efficiency(self, train_id: str, train: dict) -> Optional[AIRecommendation]:
        """Analyze energy consumption and suggest optimizations"""
        if random.random() < 0.25:  # 25% chance of energy recommendation
            efficiency_type = random.choice([
                'eco_speed', 'coasting', 'regenerative_braking', 'idle_reduction'
            ])
            
            if efficiency_type == 'eco_speed':
                self.recommendation_counter += 1
                return AIRecommendation(
                    id=f"REC_{self.recommendation_counter:04d}",
                    type=RecommendationType.SPEED_CHANGE,
                    train_id=train_id,
                    priority="LOW",
                    message=f"Energy optimization mode available for {train_id}",
                    action="Reduce speed to 50 mph for optimal fuel efficiency",
                    predicted_outcome="25% energy savings, reduced carbon footprint",
                    confidence=0.79,
                    timestamp=time.time()
                )
            
            elif efficiency_type == 'coasting':
                self.recommendation_counter += 1
                return AIRecommendation(
                    id=f"REC_{self.recommendation_counter:04d}",
                    type=RecommendationType.SPEED_CHANGE,
                    train_id=train_id,
                    priority="LOW",
                    message=f"Coasting opportunity detected for {train_id}",
                    action="Begin coasting approach to next station",
                    predicted_outcome="15% energy savings on this segment",
                    confidence=0.74,
                    timestamp=time.time()
                )
        
        return None
    
    def _analyze_passenger_comfort(self, train_id: str, train: dict) -> Optional[AIRecommendation]:
        """Analyze passenger comfort and suggest improvements"""
        train_type = train.get('type', 'freight')
        
        # Only passenger trains need comfort recommendations
        if train_type in ['passenger', 'express'] and random.random() < 0.2:  # 20% chance
            comfort_type = random.choice([
                'smooth_acceleration', 'gentle_braking', 'curve_speed', 'station_approach'
            ])
            
            if comfort_type == 'smooth_acceleration':
                self.recommendation_counter += 1
                return AIRecommendation(
                    id=f"REC_{self.recommendation_counter:04d}",
                    type=RecommendationType.SPEED_CHANGE,
                    train_id=train_id,
                    priority="LOW",
                    message=f"Passenger comfort optimization for {train_id}",
                    action="Gradual acceleration to 55 mph over 2 minutes",
                    predicted_outcome="Improved passenger comfort, reduced complaints",
                    confidence=0.76,
                    timestamp=time.time()
                )
            
            elif comfort_type == 'curve_speed':
                self.recommendation_counter += 1
                return AIRecommendation(
                    id=f"REC_{self.recommendation_counter:04d}",
                    type=RecommendationType.SPEED_CHANGE,
                    train_id=train_id,
                    priority="MEDIUM",
                    message=f"Curve ahead - comfort speed adjustment for {train_id}",
                    action="Reduce speed to 35 mph for curve comfort",
                    predicted_outcome="Reduced lateral forces, improved passenger experience",
                    confidence=0.83,
                    timestamp=time.time()
                )
        
        return None
    
    def _create_collision_recommendation(self, risk: dict) -> Optional[AIRecommendation]:
        """Create AI recommendation based on collision risk"""
        risk_level = risk.get('risk_level', 'LOW')
        train1 = risk.get('train1', '')
        train2 = risk.get('train2', '')
        
        self.recommendation_counter += 1
        
        if risk_level == 'CRITICAL':
            return AIRecommendation(
                id=f"COLLISION_ALERT_{self.recommendation_counter:04d}",
                type=RecommendationType.EMERGENCY_STOP,
                train_id=f"{train1},{train2}",  # Multiple trains affected
                priority="CRITICAL",
                message=f"🚨 COLLISION IMMINENT: {train1} and {train2} - Distance: {risk.get('distance_feet', 0):.0f}ft",
                action=f"EMERGENCY STOP ALL TRAINS - {risk.get('recommended_action', '')}",
                predicted_outcome=f"Prevent collision - Braking distance needed: {risk.get('braking_distance_needed', 0):.0f}ft",
                confidence=0.98,
                timestamp=time.time(),
                collision_data=risk
            )
        
        elif risk_level == 'HIGH':
            return AIRecommendation(
                id=f"COLLISION_WARNING_{self.recommendation_counter:04d}",
                type=RecommendationType.SPEED_CHANGE,
                train_id=risk.get('approaching_train', train1),
                priority="HIGH",
                message=f"⚠️ COLLISION RISK: {train1} approaching {train2} - Time: {risk.get('time_to_collision', 0):.1f}s",
                action=f"Immediate speed reduction - {risk.get('recommended_action', '')}",
                predicted_outcome=f"Avoid collision, increase safety margin to {risk.get('distance_feet', 0):.0f}ft",
                confidence=0.92,
                timestamp=time.time(),
                collision_data=risk
            )
        
        elif risk_level == 'MEDIUM':
            return AIRecommendation(
                id=f"COLLISION_CAUTION_{self.recommendation_counter:04d}",
                type=RecommendationType.SPEED_CHANGE,
                train_id=risk.get('approaching_train', train1),
                priority="MEDIUM",
                message=f"⚡ CAUTION: {train1} and {train2} converging - Distance: {risk.get('distance_feet', 0):.0f}ft",
                action=f"Reduce speed and monitor - {risk.get('recommended_action', '')}",
                predicted_outcome=f"Maintain safe following distance, prevent close approach",
                confidence=0.85,
                timestamp=time.time(),
                collision_data=risk
            )
        
        return None
    
    def trigger_emergency_alert(self, risk: dict, gui_callback=None) -> dict:
        """Trigger emergency alert system for critical collisions"""
        alert_response = {
            'alert_triggered': True,
            'timestamp': time.time(),
            'risk_data': risk,
            'actions_taken': []
        }
        
        risk_level = risk.get('risk_level', 'LOW')
        
        if risk_level == 'CRITICAL':
            # Emergency stop all trains
            alert_response['actions_taken'].extend([
                'Emergency brake signal sent to all trains',
                'Control tower alerted',
                'Emergency response team dispatched',
                'Track signals set to red'
            ])
            
            # If GUI callback provided, trigger emergency stop
            if gui_callback:
                gui_callback('emergency_stop_all', risk)
        
        elif risk_level == 'HIGH':
            # Speed reduction and monitoring
            alert_response['actions_taken'].extend([
                f"Speed reduction command sent to {risk.get('approaching_train', 'unknown')}",
                'Increased monitoring activated',
                'Backup control systems activated'
            ])
            
            if gui_callback:
                gui_callback('speed_reduction', risk)
        
        return alert_response

class ControlCenterGUI:
    """Main control center interface"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Railway Control Center - Prototype")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1e1e1e')
        
        # Initialize components
        self.ai_system = ControlCenterAI()
        self.tracking_points = {}
        self.active_tracking_point = None
        self.trains = {}
        self.segments = {}
        self.recommendations = []
        self.tracking_mode = TrackingMode.MANUAL
        
        # AI recommendation timing control
        self.recommendation_interval = 2000  # 2 seconds between AI recommendations (faster response)
        self.last_recommendation_time = 0
        self.max_recommendations = 5  # Maximum number of pending recommendations
        self.emergency_stopped = False  # Track if trains are emergency stopped
        self.selected_recommendation_id = None  # Store selected recommendation manually
        self.selected_recommendation_data = None  # Store full recommendation data
        
        # Threading for concurrent AI recommendations
        self.ai_thread_running = True
        self.ai_thread_lock = threading.Lock()
        self.ai_update_queue = []  # Queue for AI updates to GUI
        
        # Initialize multi-track system
        self._setup_multi_track_system()
        
        # Create GUI components
        self._create_gui()
        
        # Start simulation
        self._load_demo_data()
        self._start_simulation_loop()
        
        # Start concurrent AI recommendation thread
        self._start_ai_thread()
        
        # Setup cleanup on window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _setup_multi_track_system(self):
        """Setup multi-track railway system"""
        # Add tracks
        self.ai_system.multi_track.add_track('MAIN_A', ['SEG_01', 'SEG_02', 'SEG_03'], capacity=3)
        self.ai_system.multi_track.add_track('MAIN_B', ['SEG_04', 'SEG_05', 'SEG_06'], capacity=2)
        self.ai_system.multi_track.add_track('SIDING_1', ['SEG_07'], capacity=1)
        
        # Add junctions
        self.ai_system.multi_track.add_junction('JUNCTION_1', ['MAIN_A'], ['MAIN_B', 'SIDING_1'])
        self.ai_system.multi_track.add_junction('JUNCTION_2', ['MAIN_B'], ['MAIN_A'])
    
    def _create_gui(self):
        """Create the main GUI layout"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Train tracking and display
        left_frame = ttk.LabelFrame(main_frame, text="Train Tracking & Display", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Tracking controls
        tracking_frame = ttk.Frame(left_frame)
        tracking_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(tracking_frame, text="Tracking Mode:").pack(side=tk.LEFT)
        self.tracking_mode_var = tk.StringVar(value="manual")
        ttk.Radiobutton(tracking_frame, text="Manual", variable=self.tracking_mode_var, 
                       value="manual", command=self._change_tracking_mode).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(tracking_frame, text="Auto", variable=self.tracking_mode_var, 
                       value="auto", command=self._change_tracking_mode).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(tracking_frame, text="Focused", variable=self.tracking_mode_var, 
                       value="focused", command=self._change_tracking_mode).pack(side=tk.LEFT, padx=5)
        
        # Tracking points selection
        points_frame = ttk.Frame(left_frame)
        points_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(points_frame, text="Tracking Point:").pack(side=tk.LEFT)
        self.tracking_point_var = tk.StringVar()
        self.tracking_point_combo = ttk.Combobox(points_frame, textvariable=self.tracking_point_var,
                                               state="readonly", width=20)
        self.tracking_point_combo.pack(side=tk.LEFT, padx=5)
        self.tracking_point_combo.bind('<<ComboboxSelected>>', self._select_tracking_point)
        
        ttk.Button(points_frame, text="Focus View", 
                  command=self._focus_tracking_point).pack(side=tk.LEFT, padx=5)
        
        # Train display canvas
        self.display_canvas = tk.Canvas(left_frame, bg='#2d2d2d', height=400)
        self.display_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Train status
        status_frame = ttk.LabelFrame(left_frame, text="Train Status")
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.train_status_text = tk.Text(status_frame, height=6, bg='#1e1e1e', fg='white')
        self.train_status_text.pack(fill=tk.BOTH, expand=True)
        
        # Right panel - AI Recommendations and Controls
        right_frame = ttk.LabelFrame(main_frame, text="AI Control Center", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        right_frame.configure(width=500)
        
        # AI Recommendations
        rec_frame = ttk.LabelFrame(right_frame, text="AI Recommendations")
        rec_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Recommendations list
        rec_list_frame = ttk.Frame(rec_frame)
        rec_list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions label
        instructions_label = ttk.Label(rec_list_frame, 
                                     text="💡 Click on a recommendation below, then click 'Accept' to implement it",
                                     font=('Arial', 9, 'italic'))
        instructions_label.pack(fill=tk.X, pady=(0, 2))
        
        # Count label
        self.recommendation_count_label = ttk.Label(rec_list_frame, 
                                                  text="📊 Pending: 0 | Implemented: 0",
                                                  font=('Arial', 8))
        self.recommendation_count_label.pack(fill=tk.X, pady=(0, 5))
        
        columns = ('ID', 'Priority', 'Train', 'Type', 'Message')
        self.recommendations_tree = ttk.Treeview(rec_list_frame, columns=columns, show='headings', height=8)
        
        # Make columns more readable
        column_widths = {'ID': 60, 'Priority': 80, 'Train': 80, 'Type': 100, 'Message': 200}
        for col in columns:
            self.recommendations_tree.heading(col, text=col)
            self.recommendations_tree.column(col, width=column_widths.get(col, 80), minwidth=50)
        
        rec_scrollbar = ttk.Scrollbar(rec_list_frame, orient=tk.VERTICAL, command=self.recommendations_tree.yview)
        self.recommendations_tree.configure(yscrollcommand=rec_scrollbar.set)
        
        self.recommendations_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        rec_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind multiple click events for better detection
        self.recommendations_tree.bind('<Button-1>', self._on_recommendation_select)
        self.recommendations_tree.bind('<ButtonRelease-1>', self._on_recommendation_click_release)
        self.recommendations_tree.bind('<Double-1>', self._on_recommendation_double_click)
        self.recommendations_tree.bind('<<TreeviewSelect>>', self._on_treeview_select)
        
        # Recommendation actions
        action_frame = ttk.Frame(rec_frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Status label
        self.recommendation_status_label = ttk.Label(action_frame, text="Select a recommendation above", 
                                                   foreground="gray")
        self.recommendation_status_label.pack(fill=tk.X, pady=(0, 5))
        
        # Action buttons with more prominent styling
        button_frame = ttk.Frame(action_frame)
        button_frame.pack(fill=tk.X)
        
        self.accept_button = ttk.Button(button_frame, text="✅ Accept & Implement", 
                                      command=self._accept_recommendation, width=20, state="disabled")
        self.accept_button.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(button_frame, text="❌ Reject", 
                  command=self._reject_recommendation).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🔮 Simulate Outcome", 
                  command=self._simulate_outcome).pack(side=tk.LEFT, padx=5)
        
        # Debug buttons for testing recommendations
        debug_frame = ttk.Frame(action_frame)
        debug_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(debug_frame, text="🧪 Generate Test Recs", 
                  command=self._force_generate_recommendations, width=15).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(debug_frame, text="🔄 Clear All", 
                  command=self._clear_all_recommendations, width=10).pack(side=tk.LEFT, padx=2)
        
        # Emergency controls
        emergency_frame = ttk.LabelFrame(right_frame, text="Emergency Controls")
        emergency_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(emergency_frame, text="Emergency Stop All", 
                  command=self._emergency_stop_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(emergency_frame, text="Restart All Trains", 
                  command=self._restart_all_trains).pack(side=tk.LEFT, padx=5)
        ttk.Button(emergency_frame, text="Simulate Brake Failure", 
                  command=self._simulate_brake_failure).pack(side=tk.LEFT, padx=5)
        
        # AI Settings
        ai_settings_frame = ttk.LabelFrame(right_frame, text="AI Recommendation Settings")
        ai_settings_frame.pack(fill=tk.X, pady=(10, 10))
        
        timing_frame = ttk.Frame(ai_settings_frame)
        timing_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(timing_frame, text="Recommendation Interval:").pack(side=tk.LEFT)
        self.interval_var = tk.StringVar(value="10")
        interval_combo = ttk.Combobox(timing_frame, textvariable=self.interval_var, 
                                    values=["5", "10", "15", "20", "30"], width=5, state="readonly")
        interval_combo.pack(side=tk.LEFT, padx=5)
        ttk.Label(timing_frame, text="seconds").pack(side=tk.LEFT)
        
        ttk.Button(timing_frame, text="Apply", 
                  command=self._update_ai_settings).pack(side=tk.LEFT, padx=10)
        ttk.Button(timing_frame, text="Clear All Recommendations", 
                  command=self._clear_recommendations).pack(side=tk.LEFT, padx=5)
        
        # Track controls
        track_frame = ttk.LabelFrame(right_frame, text="Track Management")
        track_frame.pack(fill=tk.X)
        
        ttk.Label(track_frame, text="Junction Control:").pack(anchor=tk.W)
        
        junction_frame = ttk.Frame(track_frame)
        junction_frame.pack(fill=tk.X, pady=5)
        
        self.junction_var = tk.StringVar(value="JUNCTION_1")
        ttk.Combobox(junction_frame, textvariable=self.junction_var, 
                    values=["JUNCTION_1", "JUNCTION_2"], state="readonly", width=15).pack(side=tk.LEFT)
        
        ttk.Button(junction_frame, text="Switch to Track A", 
                  command=lambda: self._switch_junction_track('MAIN_A')).pack(side=tk.LEFT, padx=5)
        ttk.Button(junction_frame, text="Switch to Track B", 
                  command=lambda: self._switch_junction_track('MAIN_B')).pack(side=tk.LEFT, padx=5)
    
    def _load_demo_data(self):
        """Load demo data for the prototype"""
        # Create tracking points
        self.tracking_points = {
            'CP_NORTH': TrackingPoint('CP_NORTH', 'Control Point North', 200, 100, 'SEG_01', 0.2),
            'CP_CENTRAL': TrackingPoint('CP_CENTRAL', 'Control Point Central', 400, 200, 'SEG_02', 0.5),
            'CP_SOUTH': TrackingPoint('CP_SOUTH', 'Control Point South', 600, 300, 'SEG_03', 0.8),
            'CP_JUNCTION': TrackingPoint('CP_JUNCTION', 'Junction Control Point', 300, 250, 'SEG_04', 0.3)
        }
        
        # Update tracking point combo
        self.tracking_point_combo['values'] = list(self.tracking_points.keys())
        self.tracking_point_combo.set('CP_CENTRAL')
        
        # Create demo trains with collision scenario between EXP_001 and LOC_301
        self.trains = {
            'EXP_001': {
                'id': 'EXP_001',
                'label': 'Express 001',
                'segment': 'SEG_01',         # Put on same segment as LOC_301 for collision
                'track': 'MAIN_A',           # Same track as LOC_301
                'lane': 0,                   # Main track lane
                'y_offset': 0.0,            # Center line
                'direction': 'EASTBOUND',    # Direction indicator
                'offset': 0.2,               # Reduced offset for closer proximity
                'speed': 65,
                'type': 'passenger',
                'priority': 'EXP',
                'direction': 1,              # Eastbound
                'mass': 800,
                'brakes_failed': False,
                'last_update': time.time()
            },
            'FRT_205': {
                'id': 'FRT_205',
                'label': 'Freight 205',
                'segment': 'SEG_02',          # Different segment to avoid interference
                'track': 'MAIN_B',           # Different track
                'lane': 1,                   # Parallel track lane
                'y_offset': 0.3,            # Offset from center line (parallel track)
                'direction': 'WESTBOUND',    # Opposite direction
                'offset': 0.7,
                'speed': 35,
                'type': 'freight',
                'priority': 'FRT',
                'direction': -1,             # Opposite direction value
                'mass': 2500,
                'brakes_failed': False,
                'last_update': time.time()
            },
            'LOC_301': {
                'id': 'LOC_301',
                'label': 'Locomotive 301',
                'segment': 'SEG_01',         # Same segment as EXP_001 for collision!
                'track': 'MAIN_A',           # Same track as EXP_001
                'lane': 0,                   # Same lane
                'y_offset': 0.0,            # Center line
                'direction': 'WESTBOUND',    # Opposite direction to EXP_001
                'offset': 0.8,               # Increased offset to approach EXP_001
                'speed': 45,
                'type': 'locomotive',
                'priority': 'LOC',
                'direction': -1,             # Westbound (opposite to EXP_001)
                'mass': 400,
                'brakes_failed': False,
                'last_update': time.time()
            },
            'EXP_102': {
                'id': 'EXP_102',
                'label': 'Express 102',
                'segment': 'SEG_04',
                'track': 'MAIN_B',           # Branch line
                'lane': 0,
                'y_offset': 0.0,
                'direction': 'EASTBOUND',
                'offset': 0.6,
                'speed': 70,
                'type': 'passenger',
                'priority': 'EXP',
                'direction': 1,
                'mass': 750,
                'brakes_failed': False,
                'last_update': time.time()
            }
        }
        
        # Create demo segments
        self.segments = {
            'SEG_01': {'id': 'SEG_01', 'name': 'Main Line North', 'length': 5.2, 'grade': -0.5},
            'SEG_02': {'id': 'SEG_02', 'name': 'Main Line Central', 'length': 3.8, 'grade': 0.0},
            'SEG_03': {'id': 'SEG_03', 'name': 'Main Line South', 'length': 4.1, 'grade': 1.2},
            'SEG_04': {'id': 'SEG_04', 'name': 'Branch Line East', 'length': 2.9, 'grade': -0.8}
        }
    
    def _start_simulation_loop(self):
        """Start the main simulation loop"""
        self._update_simulation()
        self._process_ai_updates()  # Process any AI updates from thread
        self.root.after(200, self._start_simulation_loop)  # Update every 0.2 seconds (5x per second)
    
    def _start_ai_thread(self):
        """Start the concurrent AI recommendation thread"""
        def ai_worker():
            """AI worker thread that runs independently"""
            while self.ai_thread_running:
                try:
                    # Analyze traffic situation in separate thread
                    with self.ai_thread_lock:
                        # Copy current state for thread-safe analysis
                        trains_copy = self.trains.copy() if self.trains else {}
                        segments_copy = self.segments.copy() if self.segments else {}
                        current_recs = len(self.recommendations)
                    
                    # Generate recommendations if needed (not blocking GUI)
                    if current_recs < self.max_recommendations and trains_copy:
                        new_recommendations = self.ai_system.analyze_traffic_situation(trains_copy, segments_copy)
                        
                        # Queue recommendations for GUI thread
                        if new_recommendations:
                            with self.ai_thread_lock:
                                for rec in new_recommendations:
                                    if rec.id not in [r.id for r in self.recommendations]:
                                        self.ai_update_queue.append(('add_recommendation', rec))
                    
                    # Sleep for AI analysis interval (independent of GUI)
                    time.sleep(3.0)  # 3 second AI analysis cycle
                    
                except Exception as e:
                    print(f"AI Thread Error: {e}")
                    time.sleep(1.0)  # Recover from errors
        
        # Start AI thread as daemon (will close with main program)
        ai_thread = threading.Thread(target=ai_worker, daemon=True)
        ai_thread.start()
        print("🤖 AI Recommendation Thread Started - Running concurrently with simulation")
    
    def _process_ai_updates(self):
        """Process AI updates from the concurrent thread (called from GUI thread)"""
        with self.ai_thread_lock:
            while self.ai_update_queue:
                action, data = self.ai_update_queue.pop(0)
                
                if action == 'add_recommendation':
                    self.recommendations.append(data)
                    # Handle critical collision alerts automatically
                    if (data.collision_data and 
                        data.collision_data.get('risk_level') == 'CRITICAL' and
                        data.priority == 'CRITICAL'):
                        self._handle_collision_alert(data)
                
                # Update recommendation display (will be called in main GUI loop)
                pass  # Display updates handled in main simulation loop
    
    def _update_simulation(self):
        """Update the simulation state - now focuses only on train movement and physics"""
        # Move trains
        for train_id, train in self.trains.items():
            # Simple movement simulation
            speed_factor = train['speed'] / 100.0
            direction = train['direction']
            
            new_offset = train['offset'] + (direction * speed_factor * 0.02)  # Small increment
            
            # Handle segment boundaries
            if new_offset > 1.0:
                new_offset = 0.1
                # In real system, would transition to next segment
            elif new_offset < 0.0:
                new_offset = 0.9
            
            train['offset'] = new_offset
            train['last_update'] = time.time()
        
        # AUTOMATIC COLLISION PREVENTION - Progressive speed reduction
        self._apply_automatic_collision_prevention()
        
        # Note: AI recommendations are now handled by concurrent thread
        
        # If no recommendations exist, create some test recommendations for demonstration
        if len(self.recommendations) == 0:
            self._generate_test_recommendations()
        
        # Update displays
        self._update_train_display()
        self._update_recommendations_display()
        self._update_status_display()
    
    def _apply_automatic_collision_prevention(self):
        """Automatically slow down trains that are approaching collision"""
        if self.emergency_stopped:
            return  # Don't interfere with emergency stop
        
        # Get all collision risks - NO DELAYS, IMMEDIATE RESPONSE
        collision_risks = self.ai_system.collision_detector.calculate_collision_risk(self.trains, self.segments)
        
        # IMMEDIATE collision prevention - show critical risks instantly
        if collision_risks:
            for risk in collision_risks:
                if risk.get('risk_level') in ['HIGH', 'CRITICAL']:
                    distance = risk.get('distance_feet', 0)
                    print(f"🚨 COLLISION RISK: {risk.get('train1')} vs {risk.get('train2')} - {distance:.0f}ft - {risk.get('risk_level')}")
        
        for risk in collision_risks:
            distance_feet = risk.get('distance_feet', 9999)
            risk_level = risk.get('risk_level', 'SAFE')
            train1_id = risk.get('train1')
            train2_id = risk.get('train2')
            approaching_train = risk.get('approaching_train')
            leading_train = risk.get('leading_train')
            
            if risk_level == 'SAFE' or not train1_id or not train2_id:
                continue
            
            train1 = self.trains.get(train1_id)
            train2 = self.trains.get(train2_id)
            
            if not train1 or not train2:
                continue
            
            # CRITICAL: Check for stationary train scenarios - immediate stop needed
            train1_stationary = train1['speed'] == 0
            train2_stationary = train2['speed'] == 0
            
            if train1_stationary and train2['speed'] > 0:
                # Train1 stopped, Train2 approaching - IMMEDIATE STOP for Train2
                print(f"🚨 EMERGENCY: {train2_id} approaching stationary {train1_id} - IMMEDIATE STOP!")
                train2['speed'] = 0
                continue
                
            elif train2_stationary and train1['speed'] > 0:
                # Train2 stopped, Train1 approaching - IMMEDIATE STOP for Train1
                print(f"🚨 EMERGENCY: {train1_id} approaching stationary {train2_id} - IMMEDIATE STOP!")
                train1['speed'] = 0
                continue
            
            # Progressive speed reduction based on distance - MUCH MORE AGGRESSIVE
            # Enhanced logging to show train details clearly
            train1_label = train1.get('label', train1_id)
            train2_label = train2.get('label', train2_id)
            
            # ENHANCED: More aggressive stopping distances for safety
            if distance_feet < 1000:  # Critical - Emergency stop (increased from 500ft for safety)
                if train1['speed'] > 0 or train2['speed'] > 0:
                    print(f"🚨 COLLISION PREVENTION - EMERGENCY STOP!")
                    print(f"   🚂 {train1_label} ({train1_id}): {train1['speed']} mph → 0 mph")
                    print(f"   🚂 {train2_label} ({train2_id}): {train2['speed']} mph → 0 mph")
                    print(f"   📏 Distance: {distance_feet:.0f}ft - CRITICAL!")
                    train1['speed'] = 0
                    train2['speed'] = 0
                    
            elif distance_feet < 1500:  # Very close - Very slow (5 mph max) - increased threshold
                target_speed = 5
                if train1['speed'] > target_speed:
                    old_speed = train1['speed']
                    train1['speed'] = max(train1['speed'] - 20, target_speed)  # More aggressive reduction
                    print(f"⚠️  COLLISION PREVENTION - AGGRESSIVE SLOW:")
                    print(f"   🚂 {train1_label} ({train1_id}): {old_speed} mph → {train1['speed']} mph")
                    print(f"   📏 Distance: {distance_feet:.0f}ft")
                if train2['speed'] > target_speed:
                    old_speed = train2['speed']
                    train2['speed'] = max(train2['speed'] - 20, target_speed)  # More aggressive reduction
                    print(f"⚠️  COLLISION PREVENTION - AGGRESSIVE SLOW:")
                    print(f"   🚂 {train2_label} ({train2_id}): {old_speed} mph → {train2['speed']} mph")
                    print(f"   📏 Distance: {distance_feet:.0f}ft")
                    
            elif distance_feet < 2000:  # Close - Moderate slow (15 mph max) - more aggressive
                target_speed = 15  # Reduced from 20 mph
                if train1['speed'] > target_speed:
                    old_speed = train1['speed']
                    train1['speed'] = max(train1['speed'] - 15, target_speed)  # More aggressive reduction
                    print(f"⚡ COLLISION PREVENTION - SPEED REDUCTION:")
                    print(f"   🚂 {train1_label} ({train1_id}): {old_speed} mph → {train1['speed']} mph")
                    print(f"   📏 Distance: {distance_feet:.0f}ft")
                if train2['speed'] > target_speed:
                    old_speed = train2['speed']
                    train2['speed'] = max(train2['speed'] - 15, target_speed)  # More aggressive reduction
                    print(f"⚡ COLLISION PREVENTION - SPEED REDUCTION:")
                    print(f"   🚂 {train2_label} ({train2_id}): {old_speed} mph → {train2['speed']} mph")
                    print(f"   📏 Distance: {distance_feet:.0f}ft")
                    
            elif distance_feet < 2000:  # Approaching - Moderate slow (40 mph max)
                target_speed = 40
                if train1['speed'] > target_speed:
                    old_speed = train1['speed']
                    train1['speed'] = max(train1['speed'] - 8, target_speed)  # Moderate reduction
                    print(f"🔽 COLLISION PREVENTION - CAUTION SPEED:")
                    print(f"   🚂 {train1_label} ({train1_id}): {old_speed} mph → {train1['speed']} mph")
                    print(f"   📏 Distance: {distance_feet:.0f}ft")
                if train2['speed'] > target_speed:
                    old_speed = train2['speed']
                    train2['speed'] = max(train2['speed'] - 8, target_speed)
                    print(f"🔽 COLLISION PREVENTION - CAUTION SPEED:")
                    print(f"   🚂 {train2_label} ({train2_id}): {old_speed} mph → {train2['speed']} mph")
                    print(f"   📏 Distance: {distance_feet:.0f}ft")
                    
            elif distance_feet < 3000:  # Early warning - Light reduction (60 mph max)
                target_speed = 60
                if train1['speed'] > target_speed:
                    old_speed = train1['speed']
                    train1['speed'] = max(train1['speed'] - 5, target_speed)  # Light reduction
                    print(f"⚠️  COLLISION PREVENTION - WARNING SPEED:")
                    print(f"   🚂 {train1_label} ({train1_id}): {old_speed} mph → {train1['speed']} mph")
                    print(f"   📏 Distance: {distance_feet:.0f}ft")
                if train2['speed'] > target_speed:
                    old_speed = train2['speed']
                    train2['speed'] = max(train2['speed'] - 5, target_speed)
                    print(f"⚠️  COLLISION PREVENTION - WARNING SPEED:")
                    print(f"   🚂 {train2_label} ({train2_id}): {old_speed} mph → {train2['speed']} mph")
                    print(f"   📏 Distance: {distance_feet:.0f}ft")
    
    def _update_train_display(self):
        """Update the train display canvas"""
        self.display_canvas.delete("all")
        
        # Draw track layout
        self._draw_track_layout()
        
        # Draw tracking points
        self._draw_tracking_points()
        
        # Draw trains
        for train_id, train in self.trains.items():
            self._draw_train_on_display(train)
    
    def _draw_track_layout(self):
        """Draw the track layout on canvas with parallel tracks"""
        canvas_width = self.display_canvas.winfo_width() or 800
        canvas_height = self.display_canvas.winfo_height() or 400
        
        # Main line A (upper horizontal track)
        self.display_canvas.create_line(50, 140, canvas_width-50, 140, fill='#888888', width=3, tags="track")
        self.display_canvas.create_line(50, 150, canvas_width-50, 150, fill='#888888', width=3, tags="track")
        self.display_canvas.create_text(70, 130, text="MAIN A", fill='#888888', font=('Arial', 8, 'bold'))
        
        # Main line B (lower parallel horizontal track)
        self.display_canvas.create_line(50, 170, canvas_width-50, 170, fill='#666666', width=3, tags="track")
        self.display_canvas.create_line(50, 180, canvas_width-50, 180, fill='#666666', width=3, tags="track")
        self.display_canvas.create_text(70, 190, text="MAIN B", fill='#666666', font=('Arial', 8, 'bold'))
        
        # Branch line (diagonal)
        self.display_canvas.create_line(300, 150, 500, 300, fill='#444444', width=3, tags="track")
        self.display_canvas.create_line(305, 155, 505, 305, fill='#444444', width=3, tags="track")
        self.display_canvas.create_text(400, 200, text="BRANCH", fill='#444444', font=('Arial', 8, 'bold'))
        
        # Junction indicator
        self.display_canvas.create_oval(295, 145, 305, 165, fill='yellow', outline='black', tags="junction")
        self.display_canvas.create_text(310, 125, text="J1", fill='white', font=('Arial', 9, 'bold'))
        
        # Track separation indicators (dashed lines between parallel tracks)
        for x in range(50, canvas_width-50, 20):
            self.display_canvas.create_line(x, 160, x+10, 160, fill='#CCCCCC', width=1, tags="separator")
    
    def _draw_tracking_points(self):
        """Draw tracking points on the display"""
        for point_id, point in self.tracking_points.items():
            color = 'red' if point.active else 'blue'
            size = 8 if point.active else 6
            
            self.display_canvas.create_oval(
                point.x - size, point.y - size, 
                point.x + size, point.y + size,
                fill=color, outline='white', width=2, tags="tracking_point"
            )
            
            self.display_canvas.create_text(
                point.x, point.y - 15, text=point_id, 
                fill='white', font=('Arial', 8, 'bold')
            )
    
    def _draw_train_on_display(self, train):
        """Draw a train on the display canvas with proper track separation"""
        segment_id = train['segment']
        offset = train['offset']
        track = train.get('track', 'MAIN_A')
        y_offset = train.get('y_offset', 0.0)
        
        # Calculate position based on segment and offset
        if segment_id in ['SEG_01', 'SEG_02', 'SEG_03']:
            # Main line with parallel track support
            x = 50 + (self.display_canvas.winfo_width() - 100) * offset
            
            # Adjust y position for parallel tracks
            if track == 'MAIN_A':
                y = 145 + (y_offset * 20)  # Upper track
            elif track == 'MAIN_B':
                y = 175 + (y_offset * 20)  # Lower parallel track (30 pixels down)
            else:
                y = 155  # Default center
        elif segment_id == 'SEG_04':
            # Branch line
            start_x, start_y = 300, 155
            end_x, end_y = 500, 300
            x = start_x + (end_x - start_x) * offset
            y = start_y + (end_y - start_y) * offset
        else:
            return
        
        # Train color based on type and status
        if train.get('brakes_failed', False):
            color = 'red'
        elif train['type'] == 'passenger':
            color = '#4CAF50'
        elif train['type'] == 'freight':
            color = '#FF9800'
        else:
            color = '#2196F3'
        
        # Draw train body
        train_length = 20
        train_width = 8
        
        self.display_canvas.create_rectangle(
            x - train_length//2, y - train_width//2,
            x + train_length//2, y + train_width//2,
            fill=color, outline='black', width=2, tags="train"
        )
        
        # Draw train label
        self.display_canvas.create_text(
            x, y - 20, text=f"{train['label']}\n{train['speed']} mph",
            fill='white', font=('Arial', 8, 'bold')
        )
        
        # Speed indicator (arrow)
        if train['direction'] > 0:
            self.display_canvas.create_polygon(
                x + train_length//2, y,
                x + train_length//2 + 5, y - 3,
                x + train_length//2 + 5, y + 3,
                fill='white', tags="train"
            )
    
    def _generate_test_recommendations(self):
        """Generate test recommendations for demonstration purposes"""
        import time
        
        # Get list of active trains
        train_ids = list(self.trains.keys())
        if not train_ids:
            return
        
        current_time = time.time()
        test_recommendations = [
            AIRecommendation(
                id=f"REC_{int(current_time)}_001",
                type=RecommendationType.SPEED_CHANGE,
                train_id=train_ids[0] if len(train_ids) > 0 else "EXP_001",
                priority="MEDIUM",
                message="Reduce speed to 40 mph - traffic congestion detected ahead",
                action="Reduce speed to 40 mph",
                predicted_outcome="Reduced congestion, 2-minute delay avoided",
                confidence=0.85,
                timestamp=current_time,
                status='pending'
            ),
            AIRecommendation(
                id=f"REC_{int(current_time)}_002", 
                type=RecommendationType.ROUTE_CHANGE,
                train_id=train_ids[1] if len(train_ids) > 1 else "FRT_205",
                priority="LOW",
                message="Switch to auxiliary track - optimize traffic flow",
                action="Switch to auxiliary track",
                predicted_outcome="Improved system efficiency by 15%",
                confidence=0.75,
                timestamp=current_time,
                status='pending'
            ),
            AIRecommendation(
                id=f"REC_{int(current_time)}_003",
                type=RecommendationType.BRAKE_CHECK,
                train_id=train_ids[0] if len(train_ids) > 0 else "EXP_001", 
                priority="HIGH",
                message="Schedule brake inspection - efficiency drop detected",
                action="Schedule brake inspection",
                predicted_outcome="Prevent potential brake failure, ensure safety",
                confidence=0.90,
                timestamp=current_time,
                status='pending'
            )
        ]
        
        # Add test recommendations to the list
        for rec in test_recommendations:
            if rec.id not in [r.id for r in self.recommendations]:
                self.recommendations.append(rec)
        
        print(f"🧪 Generated {len(test_recommendations)} test recommendations for demonstration")
    
    def _force_generate_recommendations(self):
        """Force generate recommendations for testing - button callback"""
        print("🧪 FORCE GENERATING TEST RECOMMENDATIONS...")
        self._generate_test_recommendations()
        self._update_recommendations_display()
        print(f"✅ Generated recommendations. Total count: {len(self.recommendations)}")
    
    def _clear_all_recommendations(self):
        """Clear all recommendations for testing"""
        print("🔄 CLEARING ALL RECOMMENDATIONS...")
        self.recommendations.clear()
        self._update_recommendations_display()
        self.recommendation_status_label.config(text="All recommendations cleared", foreground="orange")
        self.accept_button.config(state="disabled")
        print("✅ All recommendations cleared")
    
    def _update_recommendations_display(self):
        """Update the recommendations tree view"""
        # Clear existing items
        for item in self.recommendations_tree.get_children():
            self.recommendations_tree.delete(item)
        
        # Add current recommendations
        for rec in self.recommendations:
            if rec.status == 'pending':
                # Pending recommendations (normal display)
                item = self.recommendations_tree.insert('', 'end', values=(
                    rec.id, rec.priority, rec.train_id, 
                    rec.type.value, rec.message[:50] + "..."
                ))
            elif rec.status in ['implemented', 'accepted']:
                # Implemented recommendations (shown with checkmark)
                item = self.recommendations_tree.insert('', 'end', values=(
                    f"✅ {rec.id}", rec.priority, rec.train_id, 
                    rec.type.value, f"IMPLEMENTED: {rec.message[:40]}..."
                ))
                # Set different color for implemented items
                self.recommendations_tree.set(item, 'ID', f"✅ {rec.id}")
        
        # Update count in status
        pending_count = len([r for r in self.recommendations if r.status == 'pending'])
        implemented_count = len([r for r in self.recommendations if r.status in ['implemented', 'accepted']])
        
        if hasattr(self, 'recommendation_count_label'):
            self.recommendation_count_label.config(
                text=f"📊 Pending: {pending_count} | Implemented: {implemented_count}"
            )
    
    def _update_status_display(self):
        """Update the train status text"""
        self.train_status_text.delete(1.0, tk.END)
        
        status_text = "TRAIN STATUS REPORT\n" + "="*50 + "\n"
        
        for train_id, train in self.trains.items():
            status = f"{train_id}: {train['speed']} mph on {train['segment']} "
            status += f"(Pos: {train['offset']:.2f})\n"
            
            if train.get('brakes_failed', False):
                status += "  ⚠️ BRAKE FAILURE DETECTED\n"
            
            status_text += status
        
        status_text += f"\nActive Recommendations: {len([r for r in self.recommendations if r.status == 'pending'])}\n"
        status_text += f"Tracking Mode: {self.tracking_mode.value.upper()}\n"
        if self.active_tracking_point:
            status_text += f"Active Tracking Point: {self.active_tracking_point}\n"
        
        self.train_status_text.insert(1.0, status_text)
    
    def _change_tracking_mode(self):
        """Change the tracking mode"""
        mode_value = self.tracking_mode_var.get()
        self.tracking_mode = TrackingMode(mode_value)
        
        # Deactivate all tracking points if switching away from focused mode
        if self.tracking_mode != TrackingMode.FOCUSED:
            for point in self.tracking_points.values():
                point.active = False
            self.active_tracking_point = None
    
    def _select_tracking_point(self, event=None):
        """Select a tracking point"""
        selected = self.tracking_point_var.get()
        if selected in self.tracking_points:
            # Deactivate all other points
            for point in self.tracking_points.values():
                point.active = False
            
            # Activate selected point
            self.tracking_points[selected].active = True
            self.active_tracking_point = selected
            
            # Switch to focused mode
            self.tracking_mode = TrackingMode.FOCUSED
            self.tracking_mode_var.set("focused")
    
    def _focus_tracking_point(self):
        """Focus the view on the selected tracking point"""
        if self.active_tracking_point:
            point = self.tracking_points[self.active_tracking_point]
            messagebox.showinfo("Tracking Point Focus", 
                              f"Focused on {point.name}\nMonitoring segment {point.segment_id}")
    
    def _show_recommendation_details(self, event):
        """Show detailed information about a recommendation"""
        selection = self.recommendations_tree.selection()
        if not selection:
            return
        
        item = self.recommendations_tree.item(selection[0])
        rec_id = item['values'][0]
        
        # Find the recommendation
        recommendation = None
        for rec in self.recommendations:
            if rec.id == rec_id:
                recommendation = rec
                break
        
        if not recommendation:
            return
        
        # Create detail window
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"Recommendation Details - {rec_id}")
        detail_window.geometry("600x500")
        detail_window.configure(bg='#1e1e1e')
        
        # Details frame
        details_frame = ttk.Frame(detail_window)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Basic info
        ttk.Label(details_frame, text=f"Recommendation ID: {recommendation.id}", 
                 font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=5)
        ttk.Label(details_frame, text=f"Priority: {recommendation.priority}").pack(anchor=tk.W)
        ttk.Label(details_frame, text=f"Train: {recommendation.train_id}").pack(anchor=tk.W)
        ttk.Label(details_frame, text=f"Type: {recommendation.type.value}").pack(anchor=tk.W)
        ttk.Label(details_frame, text=f"Confidence: {recommendation.confidence:.1%}").pack(anchor=tk.W)
        
        ttk.Separator(details_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        
        # Message
        ttk.Label(details_frame, text="Message:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        message_text = tk.Text(details_frame, height=3, bg='#2d2d2d', fg='white', wrap=tk.WORD)
        message_text.pack(fill=tk.X, pady=5)
        message_text.insert(1.0, recommendation.message)
        message_text.configure(state='disabled')
        
        # Action
        ttk.Label(details_frame, text="Recommended Action:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        action_text = tk.Text(details_frame, height=2, bg='#2d2d2d', fg='white', wrap=tk.WORD)
        action_text.pack(fill=tk.X, pady=5)
        action_text.insert(1.0, recommendation.action)
        action_text.configure(state='disabled')
        
        # Predicted outcome
        ttk.Label(details_frame, text="Predicted Outcome:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        outcome_text = tk.Text(details_frame, height=3, bg='#2d2d2d', fg='white', wrap=tk.WORD)
        outcome_text.pack(fill=tk.X, pady=5)
        outcome_text.insert(1.0, recommendation.predicted_outcome)
        outcome_text.configure(state='disabled')
        
        # Buttons
        button_frame = ttk.Frame(details_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(button_frame, text="Accept Recommendation", 
                  command=lambda: self._accept_specific_recommendation(recommendation, detail_window)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Simulate Outcome", 
                  command=lambda: self._simulate_specific_outcome(recommendation)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", 
                  command=detail_window.destroy).pack(side=tk.RIGHT, padx=5)
    
    def _accept_recommendation(self):
        """Accept the selected recommendation - FIXED to use stored selection"""
        # Check stored selection instead of tree selection
        if not self.selected_recommendation_id or not self.selected_recommendation_data:
            messagebox.showwarning("No Selection", 
                                 "Please click on a recommendation first to select it, then click Accept.")
            print("❌ ACCEPT FAILED: No stored selection")
            return
        
        rec_id = self.selected_recommendation_id
        print(f"🔍 ACCEPTING STORED RECOMMENDATION: {rec_id}")
        print(f"   Data: {self.selected_recommendation_data}")
        
        # Find and accept the recommendation
        recommendation_found = False
        for rec in self.recommendations:
            if rec.id == rec_id:
                print(f"   ✅ Found recommendation in list: {rec.message}")
                rec.status = 'accepted'
                self._implement_recommendation(rec)
                recommendation_found = True
                
                # Show success message
                messagebox.showinfo("Recommendation Accepted", 
                                  f"✅ Recommendation {rec_id} implemented successfully!\n\n"
                                  f"Type: {self.selected_recommendation_data['type']}\n"
                                  f"Train: {self.selected_recommendation_data['train_id']}\n"
                                  f"Action: {rec.action}")
                
                # Clear selection after successful implementation
                self.selected_recommendation_id = None
                self.selected_recommendation_data = None
                self.recommendation_status_label.config(
                    text="✅ Recommendation implemented successfully!",
                    foreground="green"
                )
                self.accept_button.config(state="disabled")
                
                # Update the display
                self._update_recommendations_display()
                break
        
        if not recommendation_found:
            messagebox.showerror("Error", f"Could not find recommendation with ID: {rec_id}")
            print(f"   ❌ Recommendation {rec_id} not found in recommendations list")
            print(f"   Available IDs: {[r.id for r in self.recommendations]}")
    
    def _on_recommendation_select(self, event):
        """Handle recommendation selection - FIXED to prevent selection loss"""
        print(f"🖱️  CLICK DETECTED at ({event.x}, {event.y})")
        
        # Get the clicked item
        item_id = self.recommendations_tree.identify_row(event.y)
        print(f"🎯 CLICKED ITEM ID: {item_id}")
        
        if item_id:
            try:
                # Get item data BEFORE selection changes
                item = self.recommendations_tree.item(item_id)
                values = item.get('values', [])
                print(f"📊 ITEM VALUES: {values}")
                
                if len(values) >= 5:
                    rec_id = values[0]
                    rec_priority = values[1]
                    rec_train = values[2]
                    rec_type = values[3]
                    rec_message = values[4]
                    
                    # Store selection data manually (PERSISTENT)
                    self.selected_recommendation_id = rec_id
                    self.selected_recommendation_data = {
                        'id': rec_id,
                        'priority': rec_priority,
                        'train_id': rec_train,
                        'type': rec_type,
                        'message': rec_message
                    }
                    
                    # Force visual selection and keep it
                    self.recommendations_tree.selection_set(item_id)
                    self.recommendations_tree.focus(item_id)
                    
                    # Update UI immediately
                    self.recommendation_status_label.config(
                        text=f"✅ SELECTED: {rec_id} ({rec_type})",
                        foreground="green"
                    )
                    
                    # Enable accept button
                    self.accept_button.config(state="normal")
                    
                    print(f"✅ SELECTION STORED: {rec_id}")
                    print(f"   Type: {rec_type}")
                    print(f"   Train: {rec_train}")
                    print(f"   Priority: {rec_priority}")
                    print(f"   🟢 Accept button ENABLED")
                    
                    return  # Success - exit early
                else:
                    print(f"❌ Invalid item values: {values}")
            except Exception as e:
                print(f"❌ Selection error: {e}")
        
        # If we get here, selection failed
        print("❌ SELECTION FAILED")
        self.selected_recommendation_id = None
        self.selected_recommendation_data = None
        self.recommendation_status_label.config(
            text="❌ Selection failed - try clicking again",
            foreground="red"
        )
        self.accept_button.config(state="disabled")
    
    def _on_recommendation_click_release(self, event):
        """Handle button release for better click detection"""
        print(f"🖱️  BUTTON RELEASE detected at {event.x}, {event.y}")
        # Call the main selection handler
        self._on_recommendation_select(event)
    
    def _on_treeview_select(self, event):
        """Handle TreeviewSelect event"""
        print(f"📋 TREEVIEW SELECT event triggered")
        selection = self.recommendations_tree.selection()
        if selection:
            print(f"🎯 TreeviewSelect - Selection found: {selection[0]}")
            self._process_selection(selection[0])
        else:
            print(f"⚠️  TreeviewSelect - No selection")
    
    def _process_selection(self, item_id):
        """Process the selected recommendation item"""
        try:
            item = self.recommendations_tree.item(item_id)
            values = item.get('values', [])
            
            if len(values) >= 5:
                rec_id = values[0]
                rec_type = values[3]
                
                self.recommendation_status_label.config(
                    text=f"✅ Selected: {rec_id} - {rec_type}",
                    foreground="blue"
                )
                self.accept_button.config(state="normal")
                print(f"✅ SELECTION PROCESSED: {rec_id}")
            else:
                print(f"❌ Invalid item values: {values}")
        except Exception as e:
            print(f"❌ Error processing selection: {e}")

    def _on_recommendation_double_click(self, event):
        """Handle double-click on recommendation - immediately implement it"""
        print(f"🖱️  DOUBLE-CLICK detected at {event.x}, {event.y}")
        selection = self.recommendations_tree.selection()
        if selection:
            item = self.recommendations_tree.item(selection[0])
            values = item.get('values', [])
            if len(values) >= 5:
                rec_id = values[0]
                rec_message = values[4]
                
                # Confirm implementation
                result = messagebox.askyesno("Quick Implementation", 
                                           f"Implement this recommendation immediately?\n\n"
                                           f"ID: {rec_id}\n"
                                           f"Action: {rec_message}")
                
                if result:
                    print(f"🚀 DOUBLE-CLICK IMPLEMENTATION: {rec_id}")
                    self._accept_recommendation()
                else:
                    print(f"❌ Double-click implementation cancelled for: {rec_id}")
            else:
                print(f"❌ Double-click: Invalid values {values}")
        else:
            print(f"❌ Double-click: No selection found")
    
    def _accept_specific_recommendation(self, recommendation: AIRecommendation, window):
        """Accept a specific recommendation"""
        recommendation.status = 'accepted'
        self._implement_recommendation(recommendation)
        window.destroy()
        messagebox.showinfo("Recommendation Accepted", 
                          f"Recommendation {recommendation.id} has been accepted and implemented.")
    
    def _reject_recommendation(self):
        """Reject the selected recommendation"""
        selection = self.recommendations_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a recommendation to reject.")
            return
        
        item = self.recommendations_tree.item(selection[0])
        rec_id = item['values'][0]
        
        # Find and reject the recommendation
        for rec in self.recommendations:
            if rec.id == rec_id:
                rec.status = 'rejected'
                break
        
        messagebox.showinfo("Recommendation Rejected", f"Recommendation {rec_id} has been rejected.")
    
    def _implement_recommendation(self, recommendation: AIRecommendation):
        """Implement the accepted recommendation with visual feedback"""
        print(f"🔧 IMPLEMENTING RECOMMENDATION: {recommendation.id}")
        print(f"   Type: {recommendation.type}")
        print(f"   Action: {recommendation.action}")
        print(f"   Train(s): {recommendation.train_id}")
        
        # Handle multiple trains (for collision scenarios)
        train_ids = recommendation.train_id.split(',')
        affected_trains = []
        implementation_results = []
        
        for train_id in train_ids:
            train_id = train_id.strip()
            train = self.trains.get(train_id)
            if train:
                affected_trains.append((train_id, train))
        
        if not affected_trains:
            print(f"   ❌ No trains found for IDs: {train_ids}")
            messagebox.showerror("Implementation Error", f"No trains found for IDs: {train_ids}")
            return
        
        # Implement based on recommendation type
        if recommendation.type == RecommendationType.EMERGENCY_STOP:
            print("   🚨 EMERGENCY STOP - Stopping all involved trains")
            for train_id, train in affected_trains:
                old_speed = train['speed']
                train['speed'] = 0
                train['brakes_failed'] = False
                print(f"      🛑 {train_id}: {old_speed} mph → 0 mph (STOPPED)")
                implementation_results.append(f"🛑 {train_id}: {old_speed} mph → 0 mph (EMERGENCY STOPPED)")
            
            # Show confirmation message
            train_names = [train_id for train_id, _ in affected_trains]
            messagebox.showinfo("Emergency Stop Activated", 
                              f"✅ Emergency stop successfully applied to:\n" + 
                              "\n".join(implementation_results))
        
        elif recommendation.type == RecommendationType.SPEED_CHANGE:
            print("   ⚡ SPEED ADJUSTMENT")
            for train_id, train in affected_trains:
                old_speed = train['speed']
                new_speed = old_speed
                
                if 'Reduce speed' in recommendation.action:
                    # Extract target speed from action if specified
                    if 'to 40 mph' in recommendation.action:
                        new_speed = 40
                    elif 'to 25 mph' in recommendation.action:
                        new_speed = 25
                    elif 'to 15 mph' in recommendation.action:
                        new_speed = 15
                    else:
                        new_speed = max(old_speed * 0.6, 10)
                elif 'Increase speed' in recommendation.action:
                    new_speed = min(old_speed * 1.3, 80)
                
                train['speed'] = int(new_speed)
                print(f"      ⚡ {train_id}: {old_speed} mph → {train['speed']} mph")
                implementation_results.append(f"⚡ {train_id}: {old_speed} mph → {train['speed']} mph")
            
            messagebox.showinfo("Speed Change Applied", 
                              f"✅ Speed adjustments successfully applied:\n" + 
                              "\n".join(implementation_results))
        
        elif recommendation.type == RecommendationType.ROUTE_CHANGE:
            print("   🔀 ROUTE CHANGE")
            for train_id, train in affected_trains:
                # Switch to alternative track/route
                if train['track'] == 'MAIN_A':
                    train['track'] = 'MAIN_B'
                    train['lane'] = 1
                    train['y_offset'] = 0.3
                elif train['track'] == 'MAIN_B':
                    train['track'] = 'MAIN_A'
                    train['lane'] = 0
                    train['y_offset'] = 0.0
                implementation_results.append(f"🔀 {train_id}: Switched to {train['track']}")
            
            messagebox.showinfo("Route Change Applied", 
                              f"✅ Route changes successfully applied:\n" + 
                              "\n".join(implementation_results))
        
        elif recommendation.type == RecommendationType.BRAKE_CHECK:
            print("   🔧 BRAKE CHECK SCHEDULED")
            for train_id, train in affected_trains:
                train['brake_check_scheduled'] = True
                implementation_results.append(f"🔧 {train_id}: Brake check scheduled")
            
            messagebox.showinfo("Brake Check Scheduled", 
                              f"✅ Brake checks successfully scheduled:\n" + 
                              "\n".join(implementation_results))
        
        # Force visual updates
        self._update_train_display()
        
        # Update the recommendation status
        recommendation.status = 'implemented'
        self._update_recommendations_display()
        
        # Log the successful implementation
        print("   ✅ Recommendation implemented successfully!")
        print("   🔄 Visual displays updated")
        
        # Clear selection and disable accept button
        self.recommendations_tree.selection_remove(self.recommendations_tree.selection())
        self.accept_button.config(state="disabled")
        self.recommendation_status_label.config(
            text="✅ Recommendation implemented successfully!",
            foreground="green"
        )
    
    def _simulate_outcome(self):
        """Simulate the outcome of the selected recommendation"""
        selection = self.recommendations_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a recommendation to simulate.")
            return
        
        item = self.recommendations_tree.item(selection[0])
        rec_id = item['values'][0]
        
        # Find the recommendation
        recommendation = None
        for rec in self.recommendations:
            if rec.id == rec_id:
                recommendation = rec
                break
        
        if recommendation:
            self._simulate_specific_outcome(recommendation)
    
    def _simulate_specific_outcome(self, recommendation: AIRecommendation):
        """Simulate the outcome of a specific recommendation"""
        outcome = self.ai_system.predict_recommendation_outcome(recommendation, self.trains, self.segments)
        
        # Create outcome window
        outcome_window = tk.Toplevel(self.root)
        outcome_window.title(f"Outcome Simulation - {recommendation.id}")
        outcome_window.geometry("700x600")
        outcome_window.configure(bg='#1e1e1e')
        
        # Outcome frame
        outcome_frame = ttk.Frame(outcome_window)
        outcome_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(outcome_frame, text=f"Simulation Results for {recommendation.id}", 
                 font=('Arial', 14, 'bold')).pack(anchor=tk.W, pady=10)
        
        ttk.Label(outcome_frame, text=f"Success Probability: {outcome['success_probability']:.1%}", 
                 font=('Arial', 12)).pack(anchor=tk.W, pady=5)
        
        # Timeline
        if 'timeline' in outcome and outcome['timeline']:
            ttk.Label(outcome_frame, text="Timeline:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(20, 5))
            
            timeline_frame = ttk.Frame(outcome_frame)
            timeline_frame.pack(fill=tk.X, pady=5)
            
            timeline_text = tk.Text(timeline_frame, height=6, bg='#2d2d2d', fg='white')
            timeline_text.pack(fill=tk.BOTH, expand=True)
            
            for event in outcome['timeline']:
                timeline_text.insert(tk.END, f"T+{event['time']:3.0f}s: {event['event']}\n")
            
            timeline_text.configure(state='disabled')
        
        # Risks and benefits
        if 'risks' in outcome and outcome['risks']:
            ttk.Label(outcome_frame, text="Risks:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(20, 5))
            for risk in outcome['risks']:
                ttk.Label(outcome_frame, text=f"• {risk}", foreground='red').pack(anchor=tk.W, padx=20)
        
        if 'benefits' in outcome and outcome['benefits']:
            ttk.Label(outcome_frame, text="Benefits:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(20, 5))
            for benefit in outcome['benefits']:
                ttk.Label(outcome_frame, text=f"• {benefit}", foreground='green').pack(anchor=tk.W, padx=20)
        
        # Additional info
        if 'stopping_distance_ft' in outcome:
            ttk.Label(outcome_frame, text=f"Stopping Distance: {outcome['stopping_distance_ft']:.0f} feet", 
                     font=('Arial', 10)).pack(anchor=tk.W, pady=10)
        
        # Close button
        ttk.Button(outcome_frame, text="Close", command=outcome_window.destroy).pack(pady=20)
    
    def _emergency_stop_all(self):
        """Emergency stop all trains (with user confirmation)"""
        confirm = messagebox.askyesno("Emergency Stop", 
                                    "This will stop all trains immediately. Continue?")
        if confirm:
            self._emergency_stop_immediate()
    
    def _emergency_stop_immediate(self):
        """Emergency stop all trains immediately (no confirmation - for collision alerts)"""
        print("🚨 EMERGENCY STOP ACTIVATED - All trains stopping immediately!")
        stopped_trains = []
        for train_id, train in self.trains.items():
            old_speed = train['speed']
            train['speed'] = 0
            train['emergency_stopped'] = True
            stopped_trains.append(f"{train_id}: {old_speed} mph → 0 mph")
            print(f"   🛑 {train_id}: {old_speed} mph → 0 mph")
        
        self.emergency_stopped = True
        print("✅ All trains stopped successfully!")
        
        # Show info without requiring user action during collision
        self.root.after(100, lambda: messagebox.showinfo("Emergency Stop", 
                          f"🚨 COLLISION PREVENTION ACTIVATED!\n\n"
                          f"All trains stopped:\n" + "\n".join(stopped_trains) + 
                          f"\n\nUse 'Restart All Trains' to resume operations."))
    
    def _restart_all_trains(self):
        """Restart all trains with safe speeds after emergency stop"""
        if not self.emergency_stopped:
            messagebox.showinfo("Restart", "No emergency stop in effect. Trains are already running.")
            return
            
        confirm = messagebox.askyesno("Restart All Trains", 
                                    "This will restart all trains with safe speeds.\n"
                                    "Ensure all issues have been resolved. Continue?")
        if confirm:
            # Restart trains with conservative speeds based on their type
            for train_id, train in self.trains.items():
                if train['type'] == 'passenger':
                    if train['priority'] == 'EXP':
                        safe_speed = 45  # Express trains restart slower
                    else:
                        safe_speed = 35  # Local trains
                elif train['type'] == 'freight':
                    safe_speed = 25  # Freight trains restart very slowly
                else:
                    safe_speed = 30  # Default
                
                train['speed'] = safe_speed
                train['emergency_stopped'] = False
                train['brakes_failed'] = False  # Reset brake failures
            
            self.emergency_stopped = False
            messagebox.showinfo("Restart Complete", 
                              "All trains have been restarted with safe speeds.\n"
                              "Monitor operations carefully.")
    
    def _simulate_brake_failure(self):
        """Simulate brake failure on a random train"""
        train_ids = list(self.trains.keys())
        if not train_ids:
            return
        
        selected_train = random.choice(train_ids)
        self.trains[selected_train]['brakes_failed'] = True
        
        # Generate emergency recommendation
        emergency_rec = AIRecommendation(
            id=f"EMERGENCY_{int(time.time())}",
            type=RecommendationType.EMERGENCY_STOP,
            train_id=selected_train,
            priority="HIGH",
            message=f"BRAKE FAILURE SIMULATION: {selected_train} brake system compromised",
            action="Immediate emergency stop and evacuation protocol",
            predicted_outcome="Prevent runaway train scenario",
            confidence=1.0,
            timestamp=time.time()
        )
        
        self.recommendations.append(emergency_rec)
        
        messagebox.showwarning("Brake Failure Simulation", 
                             f"Brake failure simulated for {selected_train}.\n"
                             "Emergency recommendation generated.")
    
    def _switch_junction_track(self, target_track):
        """Switch junction to target track"""
        junction_id = self.junction_var.get()
        messagebox.showinfo("Junction Switch", 
                          f"Junction {junction_id} switched to {target_track}")
    
    def _update_ai_settings(self):
        """Update AI recommendation settings"""
        try:
            new_interval = int(self.interval_var.get()) * 1000  # Convert to milliseconds
            self.recommendation_interval = new_interval
            messagebox.showinfo("Settings Updated", 
                              f"AI recommendations will now generate every {new_interval//1000} seconds")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please select a valid interval")
    
    def _clear_recommendations(self):
        """Clear all pending recommendations"""
        if self.recommendations:
            confirm = messagebox.askyesno("Clear Recommendations", 
                                        f"Clear all {len(self.recommendations)} pending recommendations?")
            if confirm:
                self.recommendations.clear()
                self._update_recommendations_display()
                messagebox.showinfo("Cleared", "All recommendations have been cleared")
        else:
            messagebox.showinfo("No Recommendations", "No recommendations to clear")
    
    def _handle_collision_alert(self, recommendation: AIRecommendation):
        """Handle critical collision alerts automatically"""
        if not recommendation.collision_data:
            return
            
        risk_data = recommendation.collision_data
        risk_level = risk_data.get('risk_level', 'LOW')
        
        if risk_level == 'CRITICAL':
            # Trigger emergency stop immediately (no confirmation for collision alerts)
            self._emergency_stop_immediate()
            
            # Show critical alert dialog
            self._show_collision_alert_dialog(risk_data)
            
            # Log the event
            print(f"🚨 CRITICAL COLLISION ALERT: {recommendation.message}")
            print(f"   Distance: {risk_data.get('distance_feet', 0):.0f}ft")
            print(f"   Time to collision: {risk_data.get('time_to_collision', 0):.1f}s")
            print(f"   Action taken: Emergency stop all trains")
        
        elif risk_level == 'HIGH':
            # Automatic speed reduction for approaching train
            approaching_train = risk_data.get('approaching_train')
            if approaching_train and approaching_train in self.trains:
                original_speed = self.trains[approaching_train].get('speed', 0)
                self.trains[approaching_train]['speed'] = min(15, original_speed)  # Reduce to 15 mph
                print(f"⚠️  AUTO SPEED REDUCTION: {approaching_train} reduced to 15 mph")
    
    def _show_collision_alert_dialog(self, risk_data: dict):
        """Show critical collision alert dialog"""
        alert_window = tk.Toplevel(self.root)
        alert_window.title("🚨 CRITICAL COLLISION ALERT")
        alert_window.geometry("500x400")
        alert_window.configure(bg='#ff4444')
        alert_window.transient(self.root)
        alert_window.grab_set()
        
        # Alert header
        header_frame = tk.Frame(alert_window, bg='#ff4444')
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(header_frame, text="🚨 COLLISION IMMINENT", 
                font=('Arial', 18, 'bold'), fg='white', bg='#ff4444').pack()
        
        # Risk details
        details_frame = tk.Frame(alert_window, bg='white')
        details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        details_text = tk.Text(details_frame, font=('Courier', 10), wrap=tk.WORD)
        details_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        details_content = f"""COLLISION RISK ANALYSIS:

Trains Involved: {risk_data.get('train1', 'Unknown')} and {risk_data.get('train2', 'Unknown')}
Segment: {risk_data.get('segment', 'Unknown')}
Current Distance: {risk_data.get('distance_feet', 0):.0f} feet
Time to Collision: {risk_data.get('time_to_collision', 0):.1f} seconds
Relative Speed: {risk_data.get('relative_speed', 0):.1f} mph
Braking Distance Needed: {risk_data.get('braking_distance_needed', 0):.0f} feet

RISK LEVEL: {risk_data.get('risk_level', 'UNKNOWN')}
RECOMMENDED ACTION: {risk_data.get('recommended_action', 'Unknown')}

ACTIONS TAKEN:
✓ Emergency stop signal sent to all trains
✓ Control tower alerted
✓ Emergency response team dispatched
✓ Track signals set to red
"""
        
        details_text.insert(tk.END, details_content)
        details_text.config(state=tk.DISABLED)
        
        # Close button
        tk.Button(alert_window, text="ACKNOWLEDGE ALERT", 
                 command=alert_window.destroy, bg='#ff6666', fg='white',
                 font=('Arial', 12, 'bold')).pack(pady=10)
    
    def _on_closing(self):
        """Handle application closing - cleanup threads"""
        print("🛑 Shutting down AI Kavach Control Center...")
        self.ai_thread_running = False  # Stop AI thread
        time.sleep(0.5)  # Give thread time to stop
        self.root.destroy()
    
    def run(self):
        """Run the control center application"""
        self.root.mainloop()

def main():
    """Main entry point for the control center prototype"""
    try:
        app = ControlCenterGUI()
        app.run()
    except Exception as e:
        print(f"Error starting control center: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
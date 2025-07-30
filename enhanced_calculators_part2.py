# Enhanced Calculator Suite - Part 2: Additional Financial & Tax Calculators
# This file contains the remaining enhanced calculators to be integrated into app_enhanced.py

# ===========================================
# ENHANCED TIP CALCULATOR
# ===========================================

@register_calculator
class TipCalculator(BaseCalculator):
    def __init__(self):
        super().__init__()
        self.related_calculators = ['percentage', 'salestax']
    
    def calculate(self, inputs):
        try:
            # Validate inputs
            bill_amount = self.validate_positive_number(inputs.get('bill_amount'), 'Bill Amount')
            tip_percentage = self.validate_percentage(inputs.get('tip_percentage'), 'Tip Percentage', 0, 100)
            number_of_people = int(self.validate_positive_number(inputs.get('number_of_people', 1), 'Number of People'))
            
            if self.errors:
                return {'errors': self.errors}
            
            # Optional inputs
            tax_amount = float(inputs.get('tax_amount', 0))
            service_quality = inputs.get('service_quality', 'good')
            restaurant_type = inputs.get('restaurant_type', 'casual')
            round_to_nearest = float(inputs.get('round_to_nearest', 0))
            
            # Calculate tip amount
            tip_amount = bill_amount * (tip_percentage / 100)
            total_amount = bill_amount + tip_amount + tax_amount
            
            # Calculate per person amounts
            amount_per_person = total_amount / number_of_people
            tip_per_person = tip_amount / number_of_people
            bill_per_person = bill_amount / number_of_people
            
            # Apply rounding if requested
            if round_to_nearest > 0:
                total_amount = round(total_amount / round_to_nearest) * round_to_nearest
                amount_per_person = total_amount / number_of_people
            
            # Get tipping recommendations
            tipping_guide = self._get_tipping_guide(restaurant_type, service_quality)
            tip_scenarios = self._calculate_tip_scenarios(bill_amount, tax_amount)
            
            # Add contextual tips
            self._add_tipping_insights(tip_percentage, restaurant_type, service_quality)
            
            return {
                'bill_amount': round(bill_amount, 2),
                'tip_percentage': tip_percentage,
                'tip_amount': round(tip_amount, 2),
                'tax_amount': round(tax_amount, 2),
                'total_amount': round(total_amount, 2),
                'number_of_people': number_of_people,
                'amount_per_person': round(amount_per_person, 2),
                'tip_per_person': round(tip_per_person, 2),
                'bill_per_person': round(bill_per_person, 2),
                'effective_tip_rate': round((tip_amount / (bill_amount + tax_amount)) * 100, 2) if (bill_amount + tax_amount) > 0 else 0,
                'tipping_guide': tipping_guide,
                'tip_scenarios': tip_scenarios,
                'bill_breakdown': {
                    'subtotal': round(bill_amount, 2),
                    'tax': round(tax_amount, 2),
                    'tip': round(tip_amount, 2),
                    'total': round(total_amount, 2)
                },
                'cultural_info': self._get_cultural_tipping_info(),
                'warnings': self.warnings,
                'tips': self.tips,
                'explanation': self.get_explanation(),
                'inputs': inputs
            }
            
        except Exception as e:
            return {'error': f"Calculation error: {str(e)}"}
    
    def _get_tipping_guide(self, restaurant_type, service_quality):
        """Get tipping recommendations based on context"""
        base_tips = {
            'fast_food': {'poor': 0, 'fair': 0, 'good': 0, 'excellent': 5},
            'casual': {'poor': 10, 'fair': 15, 'good': 18, 'excellent': 22},
            'fine_dining': {'poor': 15, 'fair': 18, 'good': 20, 'excellent': 25},
            'buffet': {'poor': 5, 'fair': 8, 'good': 10, 'excellent': 15},
            'takeout': {'poor': 0, 'fair': 0, 'good': 10, 'excellent': 15},
            'delivery': {'poor': 10, 'fair': 15, 'good': 18, 'excellent': 22}
        }
        
        recommended_tip = base_tips.get(restaurant_type, base_tips['casual']).get(service_quality, 18)
        
        return {
            'restaurant_type': restaurant_type,
            'service_quality': service_quality,
            'recommended_percentage': recommended_tip,
            'range': f"{max(recommended_tip-2, 0)}-{recommended_tip+3}%",
            'explanation': self._get_tip_explanation(restaurant_type, service_quality, recommended_tip)
        }
    
    def _calculate_tip_scenarios(self, bill_amount, tax_amount):
        """Calculate various tip percentage scenarios"""
        scenarios = []
        tip_percentages = [10, 15, 18, 20, 22, 25]
        
        for tip_pct in tip_percentages:
            tip_amount = bill_amount * (tip_pct / 100)
            total = bill_amount + tip_amount + tax_amount
            
            scenarios.append({
                'percentage': tip_pct,
                'tip_amount': round(tip_amount, 2),
                'total_amount': round(total, 2),
                'description': self._get_tip_description(tip_pct)
            })
        
        return scenarios
    
    def _get_tip_explanation(self, restaurant_type, service_quality, recommended_tip):
        """Explain the recommended tip"""
        explanations = {
            'fast_food': "Tipping not typically expected at fast food restaurants",
            'casual': f"Standard tip for {service_quality} service at casual dining",
            'fine_dining': f"Higher service standards warrant {recommended_tip}% for {service_quality} service",
            'buffet': "Lower tip acceptable since you serve yourself",
            'takeout': "Small tip appreciated for takeout preparation",
            'delivery': "Tip based on distance, weather, and service quality"
        }
        return explanations.get(restaurant_type, "Standard restaurant tipping guidelines")
    
    def _get_tip_description(self, percentage):
        """Describe what each tip percentage represents"""
        descriptions = {
            10: "Minimum acceptable tip (poor service)",
            15: "Standard tip (acceptable service)",
            18: "Good tip (good service)",
            20: "Generous tip (great service)",
            22: "Very generous (excellent service)",
            25: "Exceptional tip (outstanding service)"
        }
        return descriptions.get(percentage, f"{percentage}% tip")
    
    def _get_cultural_tipping_info(self):
        """Provide cultural context for tipping"""
        return {
            'united_states': {
                'standard': "15-20% is standard, 18-22% for good service",
                'note': "Tipping is customary and expected in most service industries"
            },
            'europe': {
                'standard': "5-10% or round up bill",
                'note': "Service charge often included, additional tip optional"
            },
            'asia': {
                'standard': "Not customary, may be refused",
                'note': "Check local customs, some countries find tipping offensive"
            },
            'australia': {
                'standard': "10% for good service",
                'note': "Not obligatory, wages are higher so tips are bonuses"
            }
        }
    
    def _add_tipping_insights(self, tip_percentage, restaurant_type, service_quality):
        """Add personalized tipping insights"""
        if tip_percentage < 15 and restaurant_type in ['casual', 'fine_dining']:
            self.add_warning("Tip below standard range - consider if service was poor")
        
        if tip_percentage > 25:
            self.add_tip("Very generous tip! Make sure it's intentional")
        
        if restaurant_type == 'fine_dining' and tip_percentage < 18:
            self.add_warning("Fine dining typically expects 18-25% tips")
        
        self.add_tip("Calculate tip on pre-tax amount for most accurate percentage")
        self.add_tip("Round up to nearest dollar for easier payment")
    
    def get_explanation(self):
        return """
        The Tip Calculator helps you determine appropriate gratuity amounts based on bill total, 
        service quality, and restaurant type.
        
        **Key Features:**
        1. **Basic Tip Calculation** - Calculate tip based on percentage and bill amount
        2. **Bill Splitting** - Divide bill and tip among multiple people
        3. **Tax Handling** - Option to tip on pre-tax or post-tax amount
        4. **Service Quality Guide** - Recommended tips based on service level
        5. **Restaurant Type Guidance** - Different standards for different venues
        6. **Multiple Scenarios** - Compare different tip percentages
        7. **Cultural Context** - Tipping customs in different countries
        
        **Tipping Guidelines:**
        - **Fast Food:** 0-5% (optional)
        - **Casual Dining:** 15-20% (18% standard)
        - **Fine Dining:** 18-25% (20% standard)
        - **Delivery:** 15-22% (minimum $3-5)
        - **Takeout:** 0-15% (10% for full service)
        - **Buffet:** 8-12% (less service required)
        
        **Service Quality Scale:**
        - **Poor:** Below standard minimum
        - **Fair:** Standard minimum (15%)
        - **Good:** Expected standard (18-20%)
        - **Excellent:** Above and beyond (22-25%)
        
        **Tips for Tipping:**
        - Calculate on pre-tax amount
        - Round to nearest dollar for convenience
        - Consider service complexity and quality
        - Factor in special circumstances (large groups, special requests)
        - Remember servers often depend on tips for income
        """

# ===========================================
# ENHANCED BMI CALCULATOR
# ===========================================

@register_calculator
class BMICalculator(BaseCalculator):
    def __init__(self):
        super().__init__()
        self.related_calculators = ['percentage']
    
    def calculate(self, inputs):
        try:
            unit_system = inputs.get('unit_system', 'metric')
            age = int(self.validate_number(inputs.get('age', 30), 'Age', 1, 120))
            gender = inputs.get('gender', 'male').lower()
            
            # Validate based on unit system
            if unit_system == 'metric':
                height_cm = self.validate_positive_number(inputs.get('height'), 'Height (cm)')
                weight_kg = self.validate_positive_number(inputs.get('weight'), 'Weight (kg)')
                
                if self.errors:
                    return {'errors': self.errors}
                
                height_m = height_cm / 100
                
            else:  # imperial
                height_feet = int(self.validate_number(inputs.get('height_feet'), 'Height (feet)', 1, 8))
                height_inches = float(inputs.get('height_inches', 0))
                weight_lbs = self.validate_positive_number(inputs.get('weight'), 'Weight (lbs)')
                
                if self.errors:
                    return {'errors': self.errors}
                
                # Convert to metric
                height_cm = (height_feet * 12 + height_inches) * 2.54
                weight_kg = weight_lbs / 2.205
                height_m = height_cm / 100
            
            # Calculate BMI
            bmi = weight_kg / (height_m ** 2)
            
            # Determine BMI category
            category = self._get_bmi_category(bmi)
            
            # Calculate ideal weight range
            ideal_weight_range = self._calculate_ideal_weight_range(height_m, gender, age)
            
            # Calculate body fat estimation
            body_fat_estimate = self._estimate_body_fat(bmi, age, gender)
            
            # Calculate caloric needs
            caloric_needs = self._calculate_caloric_needs(weight_kg, height_cm, age, gender)
            
            # Generate health insights
            health_recommendations = self._get_health_recommendations(bmi, category, age, gender)
            
            # BMI trends and goals
            weight_goals = self._calculate_weight_goals(weight_kg, height_m, bmi)
            
            # Add health insights
            self._add_health_insights(bmi, category, age)
            
            return {
                'bmi': round(bmi, 1),
                'category': category,
                'height_cm': round(height_cm, 1),
                'weight_kg': round(weight_kg, 1),
                'height_m': round(height_m, 2),
                'unit_system': unit_system,
                'age': age,
                'gender': gender,
                'ideal_weight_range': ideal_weight_range,
                'body_fat_estimate': body_fat_estimate,
                'caloric_needs': caloric_needs,
                'health_recommendations': health_recommendations,
                'weight_goals': weight_goals,
                'bmi_ranges': {
                    'underweight': 'Below 18.5',
                    'normal': '18.5 - 24.9',
                    'overweight': '25.0 - 29.9',
                    'obese_class_1': '30.0 - 34.9',
                    'obese_class_2': '35.0 - 39.9',
                    'obese_class_3': '40.0 and above'
                },
                'health_risks': self._get_health_risks(category),
                'measurement_tips': self._get_measurement_tips(),
                'warnings': self.warnings,
                'tips': self.tips,
                'explanation': self.get_explanation(),
                'inputs': inputs
            }
            
        except Exception as e:
            return {'error': f"Calculation error: {str(e)}"}
    
    def _get_bmi_category(self, bmi):
        """Determine BMI category"""
        if bmi < 18.5:
            return 'Underweight'
        elif bmi < 25:
            return 'Normal weight'
        elif bmi < 30:
            return 'Overweight'
        elif bmi < 35:
            return 'Obese (Class I)'
        elif bmi < 40:
            return 'Obese (Class II)'
        else:
            return 'Obese (Class III)'
    
    def _calculate_ideal_weight_range(self, height_m, gender, age):
        """Calculate ideal weight range using multiple methods"""
        # WHO BMI method (BMI 18.5-24.9)
        who_min = 18.5 * (height_m ** 2)
        who_max = 24.9 * (height_m ** 2)
        
        # Hamwi method
        if gender == 'male':
            hamwi_ideal = 48 + 2.7 * (height_m * 100 - 152.4) / 2.54
        else:
            hamwi_ideal = 45.5 + 2.2 * (height_m * 100 - 152.4) / 2.54
        
        # Robinson method
        if gender == 'male':
            robinson_ideal = 52 + 1.9 * (height_m * 100 - 152.4) / 2.54
        else:
            robinson_ideal = 49 + 1.7 * (height_m * 100 - 152.4) / 2.54
        
        # Miller method
        if gender == 'male':
            miller_ideal = 56.2 + 1.41 * (height_m * 100 - 152.4) / 2.54
        else:
            miller_ideal = 53.1 + 1.36 * (height_m * 100 - 152.4) / 2.54
        
        return {
            'who_range': f"{who_min:.1f} - {who_max:.1f} kg",
            'hamwi_ideal': f"{max(hamwi_ideal, 0):.1f} kg",
            'robinson_ideal': f"{max(robinson_ideal, 0):.1f} kg",
            'miller_ideal': f"{max(miller_ideal, 0):.1f} kg",
            'recommended_range': f"{who_min:.1f} - {who_max:.1f} kg (WHO guidelines)"
        }
    
    def _estimate_body_fat(self, bmi, age, gender):
        """Estimate body fat percentage using BMI and demographics"""
        if gender == 'male':
            body_fat = (1.20 * bmi) + (0.23 * age) - 16.2
        else:
            body_fat = (1.20 * bmi) + (0.23 * age) - 5.4
        
        # Ensure reasonable bounds
        body_fat = max(3, min(body_fat, 50))
        
        # Categorize body fat
        if gender == 'male':
            if body_fat < 6:
                category = 'Essential fat'
            elif body_fat < 14:
                category = 'Athletic'
            elif body_fat < 18:
                category = 'Fitness'
            elif body_fat < 25:
                category = 'Average'
            else:
                category = 'Above average'
        else:
            if body_fat < 14:
                category = 'Essential fat'
            elif body_fat < 21:
                category = 'Athletic'
            elif body_fat < 25:
                category = 'Fitness'
            elif body_fat < 32:
                category = 'Average'
            else:
                category = 'Above average'
        
        return {
            'estimated_percentage': round(body_fat, 1),
            'category': category,
            'note': 'This is an estimate. DEXA scan or hydrostatic weighing provide accurate measurements.'
        }
    
    def _calculate_caloric_needs(self, weight_kg, height_cm, age, gender):
        """Calculate daily caloric needs using Mifflin-St Jeor equation"""
        if gender == 'male':
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        
        activity_levels = {
            'sedentary': 1.2,
            'lightly_active': 1.375,
            'moderately_active': 1.55,
            'very_active': 1.725,
            'extremely_active': 1.9
        }
        
        return {
            'bmr': round(bmr, 0),
            'sedentary': round(bmr * 1.2, 0),
            'lightly_active': round(bmr * 1.375, 0),
            'moderately_active': round(bmr * 1.55, 0),
            'very_active': round(bmr * 1.725, 0),
            'extremely_active': round(bmr * 1.9, 0),
            'activity_descriptions': {
                'sedentary': 'Little to no exercise',
                'lightly_active': 'Light exercise 1-3 days/week',
                'moderately_active': 'Moderate exercise 3-5 days/week',
                'very_active': 'Hard exercise 6-7 days/week',
                'extremely_active': 'Very hard exercise, physical job'
            }
        }
    
    def _get_health_recommendations(self, bmi, category, age, gender):
        """Provide health recommendations based on BMI category"""
        recommendations = {
            'Underweight': {
                'priority': 'Gain weight safely',
                'diet': 'Increase caloric intake with nutrient-dense foods',
                'exercise': 'Strength training to build muscle mass',
                'medical': 'Consult healthcare provider to rule out underlying conditions',
                'tips': ['Eat frequent, balanced meals', 'Focus on healthy fats and proteins', 'Consider weight gain supplements']
            },
            'Normal weight': {
                'priority': 'Maintain current weight',
                'diet': 'Continue balanced, nutritious eating habits',
                'exercise': 'Mix of cardio and strength training',
                'medical': 'Regular health checkups',
                'tips': ['Stay consistent with healthy habits', 'Monitor portion sizes', 'Stay active daily']
            },
            'Overweight': {
                'priority': 'Gradual weight loss (1-2 lbs/week)',
                'diet': 'Moderate calorie reduction, focus on whole foods',
                'exercise': 'Regular cardio and strength training',
                'medical': 'Monitor blood pressure and cholesterol',
                'tips': ['Create moderate calorie deficit', 'Increase daily activity', 'Track food intake']
            },
            'Obese (Class I)': {
                'priority': 'Significant weight loss needed',
                'diet': 'Structured meal planning, possible professional guidance',
                'exercise': 'Start gradually, build up intensity',
                'medical': 'Regular monitoring of health markers',
                'tips': ['Consider working with nutritionist', 'Set small, achievable goals', 'Focus on sustainable changes']
            },
            'Obese (Class II)': {
                'priority': 'Medical supervision recommended',
                'diet': 'Professional nutrition counseling advised',
                'exercise': 'Low-impact activities, gradual progression',
                'medical': 'Comprehensive health assessment needed',
                'tips': ['Work with healthcare team', 'Consider behavioral therapy', 'Focus on health over just weight']
            },
            'Obese (Class III)': {
                'priority': 'Urgent medical intervention',
                'diet': 'Medically supervised weight loss program',
                'exercise': 'Physical therapy consultation',
                'medical': 'Consider bariatric surgery consultation',
                'tips': ['Immediate medical attention', 'Comprehensive treatment plan', 'Support groups beneficial']
            }
        }
        
        return recommendations.get(category, recommendations['Normal weight'])
    
    def _calculate_weight_goals(self, current_weight_kg, height_m, current_bmi):
        """Calculate weight loss/gain goals"""
        goals = {}
        
        # Target BMI ranges
        target_bmis = [18.5, 22, 24.9]  # Low normal, middle normal, high normal
        
        for target_bmi in target_bmis:
            target_weight = target_bmi * (height_m ** 2)
            weight_change = target_weight - current_weight_kg
            
            goals[f'bmi_{target_bmi}'] = {
                'target_weight_kg': round(target_weight, 1),
                'weight_change_kg': round(weight_change, 1),
                'weeks_at_1lb_per_week': round(abs(weight_change) * 2.2, 0),
                'weeks_at_2lb_per_week': round(abs(weight_change) * 1.1, 0)
            }
        
        return goals
    
    def _get_health_risks(self, category):
        """Get health risks associated with BMI category"""
        risks = {
            'Underweight': [
                'Malnutrition', 'Weakened immune system', 'Osteoporosis',
                'Fertility issues', 'Delayed wound healing'
            ],
            'Normal weight': [
                'Minimal weight-related health risks'
            ],
            'Overweight': [
                'Type 2 diabetes risk', 'High blood pressure',
                'Heart disease risk', 'Sleep apnea'
            ],
            'Obese (Class I)': [
                'Significantly increased diabetes risk', 'Cardiovascular disease',
                'High blood pressure', 'Sleep apnea', 'Certain cancers'
            ],
            'Obese (Class II)': [
                'High diabetes risk', 'Heart disease', 'Stroke risk',
                'Sleep apnea', 'Arthritis', 'Fatty liver disease'
            ],
            'Obese (Class III)': [
                'Severe diabetes risk', 'Heart failure', 'Stroke',
                'Severe sleep apnea', 'Mobility issues', 'Reduced life expectancy'
            ]
        }
        
        return risks.get(category, [])
    
    def _get_measurement_tips(self):
        """Provide tips for accurate measurements"""
        return {
            'height': [
                'Measure without shoes',
                'Stand against a wall with feet flat',
                'Keep head level, looking straight ahead',
                'Measure at the same time of day'
            ],
            'weight': [
                'Weigh at the same time daily (morning is best)',
                'Use the same scale consistently',
                'Wear minimal clothing',
                'Weigh after using bathroom, before eating'
            ],
            'general': [
                'BMI is a screening tool, not a diagnostic',
                'Muscle weighs more than fat',
                'Consider body composition alongside BMI',
                'Consult healthcare provider for complete assessment'
            ]
        }
    
    def _add_health_insights(self, bmi, category, age):
        """Add personalized health insights"""
        if category == 'Underweight':
            self.add_warning("BMI indicates underweight. Consider consulting a healthcare provider.")
        elif category.startswith('Obese'):
            self.add_warning("BMI indicates obesity. Consider medical consultation for health assessment.")
        elif category == 'Overweight':
            self.add_tip("BMI indicates overweight. Small lifestyle changes can improve health.")
        else:
            self.add_tip("BMI is in the normal range. Focus on maintaining healthy habits.")
        
        if age > 65:
            self.add_tip("For older adults, slightly higher BMI (25-27) may be protective.")
        
        self.add_tip("BMI doesn't account for muscle mass. Consider body composition analysis.")
        self.add_tip("Waist circumference is also important for health risk assessment.")
    
    def get_explanation(self):
        return """
        The BMI (Body Mass Index) Calculator evaluates your weight relative to your height to assess 
        whether you're in a healthy weight range.
        
        **How BMI Works:**
        BMI = weight (kg) / height (m)²
        
        **BMI Categories:**
        - **Underweight:** Below 18.5
        - **Normal weight:** 18.5 - 24.9
        - **Overweight:** 25.0 - 29.9
        - **Obese Class I:** 30.0 - 34.9
        - **Obese Class II:** 35.0 - 39.9
        - **Obese Class III:** 40.0 and above
        
        **Advanced Features:**
        1. **Ideal Weight Range** - Multiple calculation methods
        2. **Body Fat Estimation** - Based on age, gender, and BMI
        3. **Caloric Needs** - Daily calorie requirements for different activity levels
        4. **Health Recommendations** - Personalized advice based on BMI category
        5. **Weight Goals** - Target weights for different BMI ranges
        6. **Health Risk Assessment** - Conditions associated with BMI ranges
        
        **Important Limitations:**
        - Doesn't distinguish between muscle and fat
        - May not be accurate for athletes, elderly, or pregnant women
        - Doesn't account for bone density or body composition
        - Different standards may apply to different ethnic groups
        
        **When to Use:**
        - Initial health screening
        - Weight management planning
        - Tracking progress over time
        - Understanding health risks
        
        **Note:** BMI is a screening tool, not a diagnostic. Always consult healthcare 
        providers for complete health assessments.
        """

# ===========================================
# ENHANCED COMPOUND INTEREST CALCULATOR
# ===========================================

@register_calculator
class CompoundInterestCalculator(BaseCalculator):
    def __init__(self):
        super().__init__()
        self.related_calculators = ['investmentreturn', 'retirement', 'savings']
    
    def calculate(self, inputs):
        try:
            # Validate inputs
            principal = self.validate_positive_number(inputs.get('principal'), 'Principal Amount')
            annual_rate = self.validate_number(inputs.get('annual_rate'), 'Annual Interest Rate', 0, 50)
            years = self.validate_positive_number(inputs.get('years'), 'Number of Years')
            compound_frequency = int(self.validate_number(inputs.get('compound_frequency', 12), 'Compounding Frequency', 1, 365))
            monthly_contribution = float(inputs.get('monthly_contribution', 0))
            
            if self.errors:
                return {'errors': self.errors}
            
            # Optional inputs
            contribution_timing = inputs.get('contribution_timing', 'end')  # 'beginning' or 'end'
            inflation_rate = float(inputs.get('inflation_rate', 2.5))
            tax_rate = float(inputs.get('tax_rate', 0))
            
            # Calculate compound interest
            monthly_rate = annual_rate / 100 / 12
            months = years * 12
            
            # Future value of principal (compound interest)
            fv_principal = principal * (1 + annual_rate / 100 / compound_frequency) ** (compound_frequency * years)
            
            # Future value of annuity (monthly contributions)
            if monthly_contribution > 0:
                if contribution_timing == 'beginning':
                    # Ordinary annuity due
                    fv_contributions = monthly_contribution * (((1 + monthly_rate) ** months - 1) / monthly_rate) * (1 + monthly_rate)
                else:
                    # Ordinary annuity
                    fv_contributions = monthly_contribution * (((1 + monthly_rate) ** months - 1) / monthly_rate)
            else:
                fv_contributions = 0
            
            total_value = fv_principal + fv_contributions
            total_contributions = principal + (monthly_contribution * months)
            total_interest = total_value - total_contributions
            
            # Calculate inflation-adjusted value
            inflation_adjusted_value = total_value / ((1 + inflation_rate / 100) ** years)
            
            # Calculate after-tax value
            after_tax_value = total_value - (total_interest * tax_rate / 100)
            
            # Generate yearly breakdown
            yearly_breakdown = self._generate_yearly_breakdown(principal, annual_rate, compound_frequency, monthly_contribution, years, contribution_timing)
            
            # Calculate different scenarios
            scenario_analysis = self._calculate_scenarios(principal, annual_rate, years, monthly_contribution)
            
            # Investment insights
            investment_insights = self._generate_investment_insights(principal, total_value, total_interest, years, annual_rate)
            
            # Add financial insights
            self._add_compound_interest_insights(annual_rate, years, monthly_contribution)
            
            return {
                'principal': round(principal, 2),
                'annual_rate': annual_rate,
                'years': years,
                'compound_frequency': compound_frequency,
                'monthly_contribution': round(monthly_contribution, 2),
                'total_value': round(total_value, 2),
                'total_contributions': round(total_contributions, 2),
                'total_interest': round(total_interest, 2),
                'interest_earned': round(total_interest, 2),
                'effective_annual_rate': round(((1 + annual_rate / 100 / compound_frequency) ** compound_frequency - 1) * 100, 3),
                'inflation_adjusted_value': round(inflation_adjusted_value, 2),
                'purchasing_power_loss': round(total_value - inflation_adjusted_value, 2),
                'after_tax_value': round(after_tax_value, 2) if tax_rate > 0 else None,
                'monthly_growth': round((total_value / months) - (total_contributions / months), 2),
                'return_multiple': round(total_value / total_contributions, 2),
                'yearly_breakdown': yearly_breakdown,
                'scenario_analysis': scenario_analysis,
                'investment_insights': investment_insights,
                'compounding_power': {
                    'years_to_double': round(72 / annual_rate, 1) if annual_rate > 0 else None,
                    'interest_on_interest': round(total_interest - (principal * annual_rate / 100 * years), 2),
                    'compound_vs_simple': round(total_interest - (principal * annual_rate / 100 * years + monthly_contribution * months * annual_rate / 100 * years / 2), 2)
                },
                'warnings': self.warnings,
                'tips': self.tips,
                'explanation': self.get_explanation(),
                'inputs': inputs
            }
            
        except Exception as e:
            return {'error': f"Calculation error: {str(e)}"}
    
    def _generate_yearly_breakdown(self, principal, annual_rate, compound_frequency, monthly_contribution, years, timing):
        """Generate year-by-year breakdown"""
        breakdown = []
        balance = principal
        total_contributions = principal
        monthly_rate = annual_rate / 100 / 12
        
        for year in range(1, int(years) + 1):
            year_start_balance = balance
            year_contributions = 0
            year_interest = 0
            
            # Calculate monthly for this year
            for month in range(12):
                # Add monthly contribution
                if monthly_contribution > 0:
                    if timing == 'beginning':
                        balance += monthly_contribution
                        year_contributions += monthly_contribution
                        total_contributions += monthly_contribution
                    
                    # Calculate interest
                    interest = balance * monthly_rate
                    balance += interest
                    year_interest += interest
                    
                    if timing == 'end':
                        balance += monthly_contribution
                        year_contributions += monthly_contribution
                        total_contributions += monthly_contribution
                else:
                    # Just compound existing balance
                    interest = balance * monthly_rate
                    balance += interest
                    year_interest += interest
            
            breakdown.append({
                'year': year,
                'starting_balance': round(year_start_balance, 2),
                'contributions': round(year_contributions, 2),
                'interest_earned': round(year_interest, 2),
                'ending_balance': round(balance, 2),
                'total_contributions': round(total_contributions, 2),
                'growth_rate': round((balance - year_start_balance) / year_start_balance * 100, 2) if year_start_balance > 0 else 0
            })
        
        return breakdown
    
    def _calculate_scenarios(self, principal, base_rate, years, monthly_contribution):
        """Calculate different rate and contribution scenarios"""
        scenarios = []
        
        # Rate scenarios
        rate_scenarios = [base_rate - 2, base_rate - 1, base_rate + 1, base_rate + 2]
        contribution_scenarios = [0, monthly_contribution * 0.5, monthly_contribution * 1.5, monthly_contribution * 2]
        
        for rate in rate_scenarios:
            if rate > 0:
                monthly_rate = rate / 100 / 12
                months = years * 12
                
                fv_principal = principal * (1 + rate / 100 / 12) ** months
                fv_contributions = monthly_contribution * (((1 + monthly_rate) ** months - 1) / monthly_rate) if monthly_contribution > 0 else 0
                total_value = fv_principal + fv_contributions
                
                scenarios.append({
                    'type': 'rate_change',
                    'parameter': f'{rate}% annual return',
                    'total_value': round(total_value, 2),
                    'difference': round(total_value - (principal + monthly_contribution * months), 2)
                })
        
        for contribution in contribution_scenarios:
            monthly_rate = base_rate / 100 / 12
            months = years * 12
            
            fv_principal = principal * (1 + base_rate / 100 / 12) ** months
            fv_contributions = contribution * (((1 + monthly_rate) ** months - 1) / monthly_rate) if contribution > 0 else 0
            total_value = fv_principal + fv_contributions
            
            scenarios.append({
                'type': 'contribution_change',
                'parameter': f'${contribution}/month contribution',
                'total_value': round(total_value, 2),
                'total_contributions': round(principal + contribution * months, 2)
            })
        
        return scenarios
    
    def _generate_investment_insights(self, principal, total_value, total_interest, years, annual_rate):
        """Generate insights about the investment growth"""
        return {
            'power_of_compounding': {
                'total_return_percentage': round((total_value - principal) / principal * 100, 1),
                'annual_compound_growth_rate': round(((total_value / principal) ** (1/years) - 1) * 100, 2),
                'doubling_time': round(72 / annual_rate, 1) if annual_rate > 0 else None,
                'money_multiplication': round(total_value / principal, 2)
            },
            'time_value_of_money': {
                'future_value': round(total_value, 2),
                'present_value_of_future_goal': round(total_value / ((1 + annual_rate/100) ** years), 2),
                'purchasing_power_today': round(total_value / ((1 + 0.025) ** years), 2)  # Assuming 2.5% inflation
            },
            'investment_efficiency': {
                'years_to_break_even': 1,  # Assuming positive returns
                'best_case_scenario': round(total_value * 1.2, 2),  # 20% better
                'worst_case_scenario': round(total_value * 0.8, 2),  # 20% worse
                'risk_vs_reward': 'Moderate' if 4 <= annual_rate <= 8 else 'High' if annual_rate > 8 else 'Low'
            }
        }
    
    def _add_compound_interest_insights(self, annual_rate, years, monthly_contribution):
        """Add personalized insights"""
        if annual_rate > 10:
            self.add_warning("Very high return rate assumption. Consider more conservative estimates.")
        elif annual_rate < 2:
            self.add_tip("Low return rate. Consider higher-yield investment options if appropriate.")
        
        if years < 5:
            self.add_tip("Short time horizon limits compounding power. Consider longer-term investing.")
        elif years > 30:
            self.add_tip("Excellent long-term horizon! Compound interest will work powerfully over time.")
        
        if monthly_contribution == 0:
            self.add_tip("Consider regular contributions to maximize compound growth.")
        else:
            self.add_tip("Regular contributions significantly boost compound growth!")
        
        self.add_tip("Start early! Time is the most powerful factor in compound interest.")
        self.add_tip("Consider tax-advantaged accounts like 401(k) or IRA for better growth.")
    
    def get_explanation(self):
        return """
        The Compound Interest Calculator demonstrates how your money grows over time through the power 
        of compounding, where you earn returns on both your principal and previously earned interest.
        
        **How Compound Interest Works:**
        1. You invest an initial amount (principal)
        2. It earns interest based on the annual rate
        3. The interest is added to your principal
        4. Next period, you earn interest on the new larger amount
        5. This cycle repeats, creating exponential growth
        
        **Advanced Features:**
        1. **Regular Contributions** - Add monthly investments
        2. **Compounding Frequency** - Daily, monthly, quarterly, or annual
        3. **Contribution Timing** - Beginning or end of period
        4. **Inflation Adjustment** - Real purchasing power analysis
        5. **Tax Considerations** - After-tax growth calculations
        6. **Scenario Analysis** - Compare different rates and contributions
        7. **Yearly Breakdown** - Year-by-year growth tracking
        
        **Key Concepts:**
        - **Rule of 72:** Time to double = 72 ÷ interest rate
        - **Effective Annual Rate:** True annual return considering compounding
        - **Future Value:** What your investment will be worth
        - **Present Value:** Today's value of future money
        
        **Factors That Maximize Growth:**
        1. **Time:** Start early, compound longer
        2. **Rate:** Higher returns (with appropriate risk)
        3. **Contributions:** Regular additions boost growth
        4. **Frequency:** More frequent compounding helps
        5. **Consistency:** Stay invested through market cycles
        
        **Real-World Applications:**
        - Retirement planning (401k, IRA)
        - Education savings (529 plans)
        - Emergency fund growth
        - Investment portfolio modeling
        - Debt payoff strategies (reverse compound interest)
        
        **Important Notes:**
        - Returns are not guaranteed and may vary
        - Consider inflation impact on purchasing power
        - Tax implications vary by account type
        - Higher returns typically involve higher risk
        """

# Continue adding more enhanced calculators...
# This is Part 2 - we'll need several more parts to complete all calculators
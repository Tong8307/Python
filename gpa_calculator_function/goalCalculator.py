from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QGroupBox, QGridLayout, QMessageBox)
from PyQt5.QtCore import Qt
from styles.gpa_styles import gpa_styles

class GoalCalculatorPage(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.current_cgpa = 0.0
        self.completed_credits = 0
        
        self.setStyleSheet(gpa_styles())
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title = QLabel("CGPA Goal Calculator")
        title.setObjectName("gpaHeader")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Calculate the GPA you need next semester to reach your target CGPA")
        desc.setObjectName("gpaSubheader")
        layout.addWidget(desc)
        
        # Input Group
        input_group = QGroupBox("Input Parameters")
        input_layout = QGridLayout(input_group)
        input_layout.setSpacing(10)
        
        # Current CGPA
        input_layout.addWidget(QLabel("Current CGPA:"), 0, 0)
        self.current_cgpa_input = QLineEdit()
        self.current_cgpa_input.setPlaceholderText("E.g. 3.25")
        input_layout.addWidget(self.current_cgpa_input, 0, 1)
        
        # Completed Credits
        input_layout.addWidget(QLabel("Completed Credits:"), 1, 0)
        self.completed_credits_input = QLineEdit()
        self.completed_credits_input.setPlaceholderText("E.g. 45")
        input_layout.addWidget(self.completed_credits_input, 1, 1)
        
        # Target CGPA
        input_layout.addWidget(QLabel("Target CGPA:"), 2, 0)
        self.target_cgpa_input = QLineEdit()
        self.target_cgpa_input.setPlaceholderText("E.g. 3.5")
        input_layout.addWidget(self.target_cgpa_input, 2, 1)
        
        # Future Credits (next semester)
        input_layout.addWidget(QLabel("Next Semester Credits:"), 3, 0)
        self.future_credits_input = QLineEdit()
        self.future_credits_input.setPlaceholderText("E.g. 15")
        input_layout.addWidget(self.future_credits_input, 3, 1)
        
        layout.addWidget(input_group)
        
        # Calculate Button
        calculate_btn = QPushButton("Calculate Required GPA")
        calculate_btn.setObjectName("calculateButton")
        calculate_btn.clicked.connect(self.calculate_required_gpa)
        layout.addWidget(calculate_btn)
        
        # Results Group (initially hidden)
        self.results_group = QGroupBox("Results")
        self.results_group.setVisible(False)
        results_layout = QVBoxLayout(self.results_group)
        
        self.required_gpa_label = QLabel()
        self.required_gpa_label.setAlignment(Qt.AlignCenter)
        self.required_gpa_label.setObjectName("resultValue")

        self.explanation_label = QLabel()
        self.explanation_label.setAlignment(Qt.AlignCenter)
        self.explanation_label.setWordWrap(True)
        
        self.scenario_label = QLabel()
        self.scenario_label.setAlignment(Qt.AlignCenter)
        self.scenario_label.setWordWrap(True)
        
        results_layout.addWidget(self.required_gpa_label)
        results_layout.addWidget(self.explanation_label)
        results_layout.addWidget(self.scenario_label)
        
        layout.addWidget(self.results_group)
        layout.addStretch()
    
    def calculate_required_gpa(self):
        try:
            # Get inputs
            current_cgpa = float(self.current_cgpa_input.text())
            completed_credits = float(self.completed_credits_input.text())
            target_cgpa = float(self.target_cgpa_input.text())
            future_credits = float(self.future_credits_input.text())
            
            # Validate inputs
            if not (0 <= current_cgpa <= 4.0) or not (0 <= target_cgpa <= 4.0):
                raise ValueError("CGPA must be between 0 and 4.0")
            if completed_credits < 0 or future_credits <= 0:
                raise ValueError("Credits must be positive numbers")
            
            # Calculate required GPA
            current_total = current_cgpa * completed_credits
            future_total = target_cgpa * (completed_credits + future_credits)
            required_gpa = (future_total - current_total) / future_credits
            
            # Clamp between 0-4.0 and round
            required_gpa = max(0.0, min(4.0, round(required_gpa, 2)))

            # Display results
            self.required_gpa_label.setText(f"Required GPA: {required_gpa:.2f}")
                
            # Set the explanation
            explanation_text = f"""To reach your target CGPA of {target_cgpa:.2f}, you need to get 
    a GPA of {required_gpa:.2f} in your next semester."""
                
            self.explanation_label.setText(explanation_text)

            # Add scenario analysis
            if required_gpa > 4.0:
                scenario = "⚠️  Target exceeds maximum GPA - recommend adjusting timeline or goal"
            elif required_gpa >= 3.7:
                scenario = "🎯 Challenging but possible! Plan for dedicated study time"
            elif required_gpa >= 3.0:
                scenario = "📚 Manageable goal! Regular review sessions will help you succeed"
            else:
                scenario = "💡 On track! Continue your current study habits to reach this target"
                
            self.scenario_label.setText(scenario)
            self.results_group.setVisible(True)
            
        except ValueError as e:
            QMessageBox.warning(self, "Input Error", f"Please check your inputs:\n{str(e)}")
    
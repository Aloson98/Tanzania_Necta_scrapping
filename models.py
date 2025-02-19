from mongoengine import Document, StringField, ReferenceField, IntField, CASCADE

class School(Document):
    """Model class for recording school details"""
    school_name = StringField()
    school_index = StringField()
    school_region = StringField(required=False)
    
    def __str__(self):
        return self.school_name


class SchoolGPA(Document):
    school = ReferenceField(School, required=True, reverse_delete_rule=CASCADE)
    result_year = IntField(required=True)
    year_gpa = IntField(required=True)
    total_passed = IntField(required=True)
    
    def __str__(self):
        return f"{self.school} - {self.year_gpa} ({self.result_year})"


class SubjectPerformance(Document):
    school = ReferenceField(School, required=True, reverse_delete_rule=CASCADE)
    result_year = IntField(required=True)
    subject_name = StringField(required=True)
    subject_gpa = IntField(required=True)
    subject_code = IntField(required=True)
    
    
    def __str__(self):
        return f"{self.subject_name} - {self.subject_gpa} ({self.result_year})"
    

class StudentSubjectResults(Document):
    """Model class for recording student results"""
    GRADE_CHOICES = ('A', 'B', 'C', 'D', 'E', 'F', 'S', 'X')
    
    school = ReferenceField(School, required=True, reverse_delete_rule=CASCADE)
    result_year = IntField(required=True)
    
    #Unique data index within the school
    data_index = IntField(required=True)

    g_studies = StringField(db_field="G/STUDIES", required=False, choices=GRADE_CHOICES) 
    geography = StringField(db_field="GEOGR", required=False, choices=GRADE_CHOICES)
    chemistry = StringField(db_field="CHEMISTRY", required=False, choices=GRADE_CHOICES)
    biology = StringField(db_field="BIOLOGY", required=False, choices=GRADE_CHOICES)
    bam = StringField(db_field="BAM", required=False, choices=GRADE_CHOICES)
    adv_math = StringField(db_field="ADV/MATHS", required=False, choices=GRADE_CHOICES)
    economics = StringField(db_field="ECONOMICS", required=False, choices=GRADE_CHOICES)
    history = StringField(db_field="HISTORY", required=False, choices=GRADE_CHOICES)
    kiswahili = StringField(db_field="KISWAHILI", required=False, choices=GRADE_CHOICES)
    english = StringField(db_field="ENGLISH", required=False, choices=GRADE_CHOICES)
    physics = StringField(db_field="PHYSICS", required=False, choices=GRADE_CHOICES)
    commerce = StringField(db_field="COMMERCE", required=False, choices=GRADE_CHOICES)
    accountancy = StringField(db_field="ACCOUNTANCY", required=False, choices=GRADE_CHOICES)
    divinity = StringField(db_field="DIVINITY", required=False, choices=GRADE_CHOICES)
    arabic = StringField(db_field="ARABIC", required=False, choices=GRADE_CHOICES)
    french = StringField(db_field="FRENCH", required=False, choices=GRADE_CHOICES)
    agriculture = StringField(db_field="AGRICULTURE", required=False, choices=GRADE_CHOICES)
    is_knowledge = StringField(db_field="IS/KNOWLEGDE", required=False, choices=GRADE_CHOICES)
    education = StringField(db_field="EDUCATION", required=False, choices=GRADE_CHOICES)
    comp_stud = StringField(db_field="COMP STUD", required=False, choices=GRADE_CHOICES)
    comp_science = StringField(db_field="COMP/SCIENCE", required=False, choices=GRADE_CHOICES)
    hn_nutrition = StringField(db_field="HN NUTRITION", required=False, choices=GRADE_CHOICES)
    phy_edu = StringField(db_field="PHY EDU", required=False, choices=GRADE_CHOICES)
    fine_art = StringField(db_field="FINE ART", required=False, choices=GRADE_CHOICES)
    
    meta = {
        'indexes': [
            {'fields': ['school', 'data_index'], 'unique': True}
        ]
    }
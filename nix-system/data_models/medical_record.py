"""
Medical Record Data Models

Standardized data structures for medical records following HL7 FHIR R4 standards.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class RecordStatus(Enum):
    """Medical record status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    AMENDED = "amended"
    DELETED = "deleted"
    ARCHIVED = "archived"


class ConfidentialityLevel(Enum):
    """HIPAA confidentiality levels"""
    NORMAL = "N"  # Normal
    RESTRICTED = "R"  # Restricted
    VERY_RESTRICTED = "V"  # Very restricted
    SUBSTANCE_ABUSE = "S"  # Substance abuse related
    MENTAL_HEALTH = "M"  # Mental health related


@dataclass
class PatientIdentifier:
    """Patient identification information"""
    patient_id: str
    medical_record_number: str
    ssn: Optional[str] = None
    drivers_license: Optional[str] = None
    passport_number: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "patient_id": self.patient_id,
            "medical_record_number": self.medical_record_number,
            "ssn": self.ssn,
            "drivers_license": self.drivers_license,
            "passport_number": self.passport_number
        }


@dataclass
class PatientDemographics:
    """Patient demographic information"""
    first_name: str
    last_name: str
    middle_name: Optional[str]
    date_of_birth: str
    gender: str
    race: Optional[str] = None
    ethnicity: Optional[str] = None
    marital_status: Optional[str] = None
    language: str = "en"

    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: str = "US"

    phone_home: Optional[str] = None
    phone_mobile: Optional[str] = None
    phone_work: Optional[str] = None
    email: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "middle_name": self.middle_name,
            "date_of_birth": self.date_of_birth,
            "gender": self.gender,
            "race": self.race,
            "ethnicity": self.ethnicity,
            "marital_status": self.marital_status,
            "language": self.language,
            "address": {
                "line1": self.address_line1,
                "line2": self.address_line2,
                "city": self.city,
                "state": self.state,
                "zip": self.zip_code,
                "country": self.country
            },
            "contact": {
                "phone_home": self.phone_home,
                "phone_mobile": self.phone_mobile,
                "phone_work": self.phone_work,
                "email": self.email
            }
        }


@dataclass
class EmergencyContact:
    """Emergency contact information"""
    name: str
    relationship: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "relationship": self.relationship,
            "phone": self.phone,
            "email": self.email,
            "address": self.address
        }


@dataclass
class InsuranceInfo:
    """Insurance information"""
    insurance_id: str
    provider: str
    plan_name: str
    policy_number: str
    group_number: Optional[str] = None
    subscriber_id: Optional[str] = None
    coverage_start: Optional[str] = None
    coverage_end: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "insurance_id": self.insurance_id,
            "provider": self.provider,
            "plan_name": self.plan_name,
            "policy_number": self.policy_number,
            "group_number": self.group_number,
            "subscriber_id": self.subscriber_id,
            "coverage_start": self.coverage_start,
            "coverage_end": self.coverage_end
        }


@dataclass
class Allergy:
    """Allergy information"""
    allergy_id: str
    allergen: str
    reaction: str
    severity: str  # mild, moderate, severe
    onset_date: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allergy_id": self.allergy_id,
            "allergen": self.allergen,
            "reaction": self.reaction,
            "severity": self.severity,
            "onset_date": self.onset_date,
            "notes": self.notes
        }


@dataclass
class Medication:
    """Current medication"""
    medication_id: str
    name: str
    dosage: str
    frequency: str
    route: str  # oral, injection, topical, etc.
    start_date: str
    end_date: Optional[str] = None
    prescriber: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "medication_id": self.medication_id,
            "name": self.name,
            "dosage": self.dosage,
            "frequency": self.frequency,
            "route": self.route,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "prescriber": self.prescriber,
            "notes": self.notes
        }


@dataclass
class VitalSigns:
    """Vital signs measurement"""
    recorded_at: str
    temperature: Optional[float] = None  # Fahrenheit
    temperature_unit: str = "F"
    heart_rate: Optional[int] = None  # BPM
    blood_pressure_systolic: Optional[int] = None  # mmHg
    blood_pressure_diastolic: Optional[int] = None  # mmHg
    respiratory_rate: Optional[int] = None  # breaths/min
    oxygen_saturation: Optional[float] = None  # percentage
    weight: Optional[float] = None  # pounds
    weight_unit: str = "lb"
    height: Optional[float] = None  # inches
    height_unit: str = "in"
    bmi: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "recorded_at": self.recorded_at,
            "temperature": {
                "value": self.temperature,
                "unit": self.temperature_unit
            },
            "heart_rate": self.heart_rate,
            "blood_pressure": {
                "systolic": self.blood_pressure_systolic,
                "diastolic": self.blood_pressure_diastolic
            },
            "respiratory_rate": self.respiratory_rate,
            "oxygen_saturation": self.oxygen_saturation,
            "weight": {
                "value": self.weight,
                "unit": self.weight_unit
            },
            "height": {
                "value": self.height,
                "unit": self.height_unit
            },
            "bmi": self.bmi
        }


@dataclass
class MedicalRecord:
    """Complete medical record"""
    record_id: str
    patient_identifier: PatientIdentifier
    demographics: PatientDemographics
    status: RecordStatus
    confidentiality: ConfidentialityLevel

    # Medical history
    allergies: List[Allergy] = field(default_factory=list)
    current_medications: List[Medication] = field(default_factory=list)
    vital_signs_history: List[VitalSigns] = field(default_factory=list)

    # Contacts
    emergency_contacts: List[EmergencyContact] = field(default_factory=list)
    primary_care_provider: Optional[str] = None

    # Insurance
    insurance_info: List[InsuranceInfo] = field(default_factory=list)

    # Metadata
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    created_by: Optional[str] = None
    last_accessed: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/transmission"""
        return {
            "record_id": self.record_id,
            "patient_identifier": self.patient_identifier.to_dict(),
            "demographics": self.demographics.to_dict(),
            "status": self.status.value,
            "confidentiality": self.confidentiality.value,
            "allergies": [a.to_dict() for a in self.allergies],
            "current_medications": [m.to_dict() for m in self.current_medications],
            "vital_signs_history": [v.to_dict() for v in self.vital_signs_history],
            "emergency_contacts": [e.to_dict() for e in self.emergency_contacts],
            "primary_care_provider": self.primary_care_provider,
            "insurance_info": [i.to_dict() for i in self.insurance_info],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "created_by": self.created_by,
            "last_accessed": self.last_accessed
        }

    def to_fhir_bundle(self) -> Dict[str, Any]:
        """Convert to HL7 FHIR R4 bundle format"""
        # Simplified FHIR bundle structure
        return {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": self.patient_identifier.patient_id,
                        "identifier": [
                            {
                                "system": "urn:oid:2.16.840.1.113883.4.1",
                                "value": self.patient_identifier.ssn
                            }
                        ],
                        "name": [
                            {
                                "family": self.demographics.last_name,
                                "given": [self.demographics.first_name]
                            }
                        ],
                        "birthDate": self.demographics.date_of_birth,
                        "gender": self.demographics.gender.lower()
                    }
                }
            ]
        }


# Example usage
if __name__ == "__main__":
    # Create patient identifier
    patient_id = PatientIdentifier(
        patient_id="patient_12345",
        medical_record_number="MRN_67890",
        ssn="123-45-6789"
    )

    # Create demographics
    demographics = PatientDemographics(
        first_name="John",
        last_name="Doe",
        middle_name="Michael",
        date_of_birth="1980-01-01",
        gender="M",
        city="Springfield",
        state="IL",
        zip_code="62701"
    )

    # Create medical record
    record = MedicalRecord(
        record_id="mr_001",
        patient_identifier=patient_id,
        demographics=demographics,
        status=RecordStatus.ACTIVE,
        confidentiality=ConfidentialityLevel.NORMAL
    )

    # Add allergy
    record.allergies.append(Allergy(
        allergy_id="allergy_001",
        allergen="Penicillin",
        reaction="Hives",
        severity="moderate"
    ))

    # Convert to dictionary
    record_dict = record.to_dict()
    print(f"Medical record created: {record.record_id}")
    print(f"Patient: {demographics.first_name} {demographics.last_name}")
    print(f"Allergies: {len(record.allergies)}")

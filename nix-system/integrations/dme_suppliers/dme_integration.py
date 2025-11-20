"""
DME (Durable Medical Equipment) Suppliers Integration

Handles integration with medical equipment suppliers, pharmacies,
and medical supply vendors for equipment ordering and tracking.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum


class DMECategory(Enum):
    """DME equipment categories"""
    MOBILITY = "mobility"  # Wheelchairs, walkers, canes
    RESPIRATORY = "respiratory"  # Oxygen, CPAP, nebulizers
    DIABETIC = "diabetic"  # Glucose monitors, insulin pumps
    HOSPITAL_BED = "hospital_bed"
    PROSTHETICS = "prosthetics"
    ORTHOTICS = "orthotics"
    MONITORING = "monitoring"  # BP monitors, pulse oximeters
    INFUSION = "infusion"  # IV pumps


class OrderStatus(Enum):
    """DME order status"""
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    IN_PROCESS = "in_process"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DENIED = "denied"


class DMESupplier:
    """
    DME Supplier Integration

    Handles:
    - Equipment ordering
    - Order tracking
    - Insurance verification
    - Delivery scheduling
    """

    def __init__(self, supplier_id: str, supplier_name: str,
                 endpoint: str, credentials: Dict[str, str]):
        """
        Initialize DME supplier integration

        Args:
            supplier_id: Unique supplier ID
            supplier_name: Supplier business name
            endpoint: API endpoint
            credentials: Authentication credentials
        """
        self.supplier_id = supplier_id
        self.supplier_name = supplier_name
        self.endpoint = endpoint
        self.credentials = credentials
        self.orders: Dict[str, Dict[str, Any]] = {}

    def check_inventory(self, hcpcs_code: str) -> Dict[str, Any]:
        """
        Check equipment availability

        Args:
            hcpcs_code: HCPCS code for equipment

        Returns:
            Inventory information
        """
        # HCPCS codes examples:
        # E0100-E0105: Canes
        # E1130-E1161: Wheelchairs
        # E0424-E0487: Oxygen equipment

        return {
            "hcpcs_code": hcpcs_code,
            "available": True,
            "quantity_in_stock": 15,
            "estimated_delivery_days": 3,
            "rental_available": True,
            "purchase_available": True,
            "pricing": {
                "rental_monthly": 75.00,
                "purchase_price": 850.00,
                "insurance_covered": True
            }
        }

    def create_order(self,
                    patient_id: str,
                    provider_id: str,
                    prescription_id: str,
                    hcpcs_code: str,
                    equipment_description: str,
                    delivery_address: Dict[str, str],
                    insurance_info: Dict[str, str],
                    rental: bool = False) -> Dict[str, Any]:
        """
        Create DME order

        Args:
            patient_id: Patient ID
            provider_id: Prescribing provider ID
            prescription_id: Prescription/order ID
            hcpcs_code: HCPCS code for equipment
            equipment_description: Description of equipment
            delivery_address: Delivery address
            insurance_info: Insurance information
            rental: True for rental, False for purchase

        Returns:
            Order confirmation
        """
        order_id = f"dme_order_{int(datetime.utcnow().timestamp())}"

        order = {
            "order_id": order_id,
            "supplier_id": self.supplier_id,
            "supplier_name": self.supplier_name,
            "patient_id": patient_id,
            "provider_id": provider_id,
            "prescription_id": prescription_id,
            "hcpcs_code": hcpcs_code,
            "equipment_description": equipment_description,
            "order_type": "rental" if rental else "purchase",
            "delivery_address": delivery_address,
            "insurance_info": insurance_info,
            "status": OrderStatus.PENDING_APPROVAL.value,
            "order_date": datetime.utcnow().isoformat(),
            "estimated_delivery": (datetime.utcnow() + timedelta(days=3)).isoformat(),
            "tracking_number": None
        }

        self.orders[order_id] = order
        return order

    def verify_insurance_coverage(self,
                                  insurance_id: str,
                                  insurance_provider: str,
                                  hcpcs_code: str,
                                  patient_diagnosis: List[str]) -> Dict[str, Any]:
        """
        Verify insurance coverage for DME

        Args:
            insurance_id: Insurance policy number
            insurance_provider: Insurance provider name
            hcpcs_code: HCPCS code for equipment
            patient_diagnosis: ICD-10 diagnosis codes

        Returns:
            Coverage verification
        """
        return {
            "covered": True,
            "insurance_id": insurance_id,
            "insurance_provider": insurance_provider,
            "hcpcs_code": hcpcs_code,
            "coverage_percentage": 80,
            "patient_responsibility": 20,
            "authorization_required": True,
            "authorization_number": f"AUTH{int(datetime.utcnow().timestamp())}",
            "coverage_period": "12 months",
            "rental_cap": 13,  # months before ownership
            "notes": "Requires prior authorization and medical necessity documentation"
        }

    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """
        Get order status

        Args:
            order_id: Order ID

        Returns:
            Order status and tracking information
        """
        order = self.orders.get(order_id)
        if not order:
            return {"error": "Order not found"}

        return {
            "order_id": order_id,
            "status": order["status"],
            "order_date": order["order_date"],
            "estimated_delivery": order["estimated_delivery"],
            "tracking_number": order.get("tracking_number"),
            "current_location": "Distribution Center - Los Angeles, CA",
            "delivery_notes": "Signature required"
        }

    def schedule_delivery(self,
                         order_id: str,
                         preferred_date: str,
                         preferred_time: str) -> Dict[str, Any]:
        """
        Schedule equipment delivery

        Args:
            order_id: Order ID
            preferred_date: Preferred delivery date
            preferred_time: Preferred delivery time window

        Returns:
            Delivery confirmation
        """
        order = self.orders.get(order_id)
        if not order:
            return {"error": "Order not found"}

        return {
            "order_id": order_id,
            "delivery_scheduled": True,
            "scheduled_date": preferred_date,
            "scheduled_time": preferred_time,
            "confirmation_number": f"DEL{int(datetime.utcnow().timestamp())}",
            "delivery_instructions": "Contact 24h before delivery"
        }

    def request_maintenance(self,
                          equipment_serial: str,
                          issue_description: str,
                          patient_contact: Dict[str, str]) -> Dict[str, Any]:
        """
        Request equipment maintenance or repair

        Args:
            equipment_serial: Equipment serial number
            issue_description: Description of issue
            patient_contact: Patient contact information

        Returns:
            Service request confirmation
        """
        service_id = f"service_{int(datetime.utcnow().timestamp())}"

        return {
            "service_request_id": service_id,
            "equipment_serial": equipment_serial,
            "issue_description": issue_description,
            "priority": "standard",
            "estimated_response_time": "24-48 hours",
            "service_type": "in_home",
            "status": "scheduled"
        }


class DMENetworkManager:
    """
    Manages network of DME suppliers

    Provides:
    - Supplier directory
    - Price comparison
    - Order routing
    - Network compliance
    """

    def __init__(self):
        """Initialize DME network manager"""
        self.suppliers: Dict[str, DMESupplier] = {}
        self.supplier_catalog: Dict[str, List[str]] = {}  # hcpcs_code -> supplier_ids

    def register_supplier(self, supplier: DMESupplier):
        """
        Register DME supplier in network

        Args:
            supplier: DME supplier instance
        """
        self.suppliers[supplier.supplier_id] = supplier

    def find_suppliers_for_equipment(self,
                                    hcpcs_code: str,
                                    patient_zip: str,
                                    max_distance_miles: int = 50) -> List[Dict[str, Any]]:
        """
        Find suppliers that carry specific equipment

        Args:
            hcpcs_code: HCPCS code
            patient_zip: Patient ZIP code
            max_distance_miles: Maximum distance

        Returns:
            List of available suppliers
        """
        available_suppliers = []

        for supplier_id, supplier in self.suppliers.items():
            inventory = supplier.check_inventory(hcpcs_code)

            if inventory["available"]:
                available_suppliers.append({
                    "supplier_id": supplier_id,
                    "supplier_name": supplier.supplier_name,
                    "distance_miles": 10,  # Would calculate based on zip codes
                    "pricing": inventory["pricing"],
                    "estimated_delivery_days": inventory["estimated_delivery_days"],
                    "rating": 4.5,
                    "review_count": 127
                })

        # Sort by distance
        available_suppliers.sort(key=lambda x: x["distance_miles"])

        return available_suppliers

    def compare_pricing(self, hcpcs_code: str) -> List[Dict[str, Any]]:
        """
        Compare pricing across suppliers

        Args:
            hcpcs_code: HCPCS code

        Returns:
            Price comparison
        """
        pricing = []

        for supplier_id, supplier in self.suppliers.items():
            inventory = supplier.check_inventory(hcpcs_code)

            if inventory["available"]:
                pricing.append({
                    "supplier_id": supplier_id,
                    "supplier_name": supplier.supplier_name,
                    "rental_monthly": inventory["pricing"]["rental_monthly"],
                    "purchase_price": inventory["pricing"]["purchase_price"],
                    "insurance_covered": inventory["pricing"]["insurance_covered"]
                })

        # Sort by purchase price
        pricing.sort(key=lambda x: x["purchase_price"])

        return pricing

    def route_order(self,
                   hcpcs_code: str,
                   patient_zip: str,
                   patient_id: str,
                   provider_id: str,
                   prescription_id: str,
                   delivery_address: Dict[str, str],
                   insurance_info: Dict[str, str]) -> Dict[str, Any]:
        """
        Automatically route order to best supplier

        Args:
            hcpcs_code: HCPCS code
            patient_zip: Patient ZIP code
            patient_id: Patient ID
            provider_id: Provider ID
            prescription_id: Prescription ID
            delivery_address: Delivery address
            insurance_info: Insurance information

        Returns:
            Order confirmation
        """
        # Find best supplier (closest with best pricing)
        suppliers = self.find_suppliers_for_equipment(hcpcs_code, patient_zip)

        if not suppliers:
            return {"error": "No suppliers available for this equipment"}

        best_supplier_id = suppliers[0]["supplier_id"]
        supplier = self.suppliers[best_supplier_id]

        # Create order
        order = supplier.create_order(
            patient_id=patient_id,
            provider_id=provider_id,
            prescription_id=prescription_id,
            hcpcs_code=hcpcs_code,
            equipment_description=f"Equipment {hcpcs_code}",
            delivery_address=delivery_address,
            insurance_info=insurance_info
        )

        return {
            "order_created": True,
            "supplier": suppliers[0],
            "order": order
        }


# Example usage
if __name__ == "__main__":
    # Create DME network manager
    network = DMENetworkManager()

    # Register suppliers
    supplier1 = DMESupplier(
        supplier_id="dme_001",
        supplier_name="MedEquip Supply Co.",
        endpoint="https://api.medequip.com/v1",
        credentials={"api_key": "med_key_123"}
    )
    network.register_supplier(supplier1)

    supplier2 = DMESupplier(
        supplier_id="dme_002",
        supplier_name="HealthGear Direct",
        endpoint="https://api.healthgear.com/v1",
        credentials={"api_key": "health_key_456"}
    )
    network.register_supplier(supplier2)

    # Check inventory
    inventory = supplier1.check_inventory("E1130")  # Wheelchair
    print(f"Inventory check: {inventory}")

    # Create order
    order = supplier1.create_order(
        patient_id="patient_12345",
        provider_id="dr_smith_001",
        prescription_id="rx_789",
        hcpcs_code="E1130",
        equipment_description="Standard Wheelchair",
        delivery_address={
            "street": "123 Main St",
            "city": "Springfield",
            "state": "IL",
            "zip": "62701"
        },
        insurance_info={
            "provider": "Medicare",
            "id": "1EG4-TE5-MK73"
        },
        rental=False
    )
    print(f"Order created: {order['order_id']}")

    # Find suppliers
    suppliers = network.find_suppliers_for_equipment("E1130", "62701")
    print(f"Found {len(suppliers)} suppliers")

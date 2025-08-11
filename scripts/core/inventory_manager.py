"""
Inventory Manager - Handles crop storage and management

This system manages the player's crop inventory, providing storage for harvested crops
before they are sold at market. Replaces the automatic selling system with strategic
inventory management.

Key Features:
- Store harvested crops by type and quantity
- Track crop quality and harvest date
- Manual selling through UI
- Inventory capacity management (future: storage buildings)
- Integration with market system for optimal selling times

Design Goals:
- Give players strategic control over sales timing
- Support future multiple crop types
- Enable storage building upgrades
- Provide clear inventory feedback in UI

Usage:
    inventory = InventoryManager(event_system)
    inventory.add_crop('corn', 15)  # Add 15 corn from harvest
    inventory.sell_crop('corn', 10, current_price)  # Sell 10 corn
    total_corn = inventory.get_crop_count('corn')
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from scripts.core.config import *


@dataclass
class CropEntry:
    """Individual crop storage entry with metadata"""
    crop_type: str
    quantity: int
    quality: float  # 0.0 to 1.0 based on growing conditions
    harvest_day: int  # Day when harvested (for spoilage tracking)
    
    def get_total_value(self, price_per_unit: float) -> float:
        """Calculate total value accounting for quality"""
        return self.quantity * price_per_unit * self.quality


class InventoryManager:
    """Manages crop storage and selling"""
    
    def __init__(self, event_system):
        """Initialize inventory manager"""
        self.event_system = event_system
        
        # Crop storage - organized by crop type
        self.crops: Dict[str, List[CropEntry]] = {
            'corn': []
        }
        
        # Storage capacity (can be upgraded with buildings)
        self.storage_capacity = 100  # Total units across all crops
        self.current_storage = 0
        
        # Register for events
        self.event_system.subscribe('crop_harvested', self._handle_crop_harvest)
        self.event_system.subscribe('sell_crops_requested', self._handle_sell_request)
        
        print("Inventory Manager initialized - Storage capacity: 100 units")
    
    def add_crop(self, crop_type: str, quantity: int, quality: float = 1.0, harvest_day: int = 1) -> bool:
        """
        Add harvested crops to inventory
        
        Args:
            crop_type: Type of crop ('corn', etc.)
            quantity: Number of units to add
            quality: Quality modifier (0.0 to 1.0)
            harvest_day: Day when harvested
            
        Returns:
            True if successfully added, False if storage full
        """
        if quantity <= 0:
            return False
        
        # Check storage capacity
        if self.current_storage + quantity > self.storage_capacity:
            # Storage full - could implement overflow handling here
            available_space = self.storage_capacity - self.current_storage
            if available_space <= 0:
                self.event_system.emit('storage_full', {
                    'attempted_quantity': quantity,
                    'available_space': 0,
                    'crop_type': crop_type
                })
                return False
            
            # Partial storage
            quantity = available_space
            self.event_system.emit('storage_nearly_full', {
                'stored_quantity': quantity,
                'overflow_quantity': quantity - available_space,
                'crop_type': crop_type
            })
        
        # Add to appropriate crop list
        if crop_type not in self.crops:
            self.crops[crop_type] = []
        
        crop_entry = CropEntry(crop_type, quantity, quality, harvest_day)
        self.crops[crop_type].append(crop_entry)
        self.current_storage += quantity
        
        # Emit inventory update
        self.event_system.emit('inventory_updated', {
            'crop_type': crop_type,
            'quantity_added': quantity,
            'total_quantity': self.get_crop_count(crop_type),
            'storage_used': self.current_storage,
            'storage_capacity': self.storage_capacity
        })
        
        print(f"Added {quantity} {crop_type} to inventory (quality: {quality:.2f})")
        return True
    
    def sell_crop(self, crop_type: str, quantity: int, price_per_unit: float) -> float:
        """
        Sell crops from inventory
        
        Args:
            crop_type: Type of crop to sell
            quantity: Number of units to sell
            price_per_unit: Current market price
            
        Returns:
            Total revenue from sale
        """
        if quantity <= 0 or crop_type not in self.crops:
            return 0.0
        
        crops_list = self.crops[crop_type]
        if not crops_list:
            return 0.0
        
        # Sell oldest crops first (FIFO)
        remaining_to_sell = quantity
        total_revenue = 0.0
        entries_to_remove = []
        
        for i, crop_entry in enumerate(crops_list):
            if remaining_to_sell <= 0:
                break
            
            if crop_entry.quantity <= remaining_to_sell:
                # Sell entire entry
                revenue = crop_entry.get_total_value(price_per_unit)
                total_revenue += revenue
                remaining_to_sell -= crop_entry.quantity
                self.current_storage -= crop_entry.quantity
                entries_to_remove.append(i)
                
            else:
                # Partial sale from this entry
                sold_quantity = remaining_to_sell
                revenue = sold_quantity * price_per_unit * crop_entry.quality
                total_revenue += revenue
                
                # Update entry
                crop_entry.quantity -= sold_quantity
                self.current_storage -= sold_quantity
                remaining_to_sell = 0
        
        # Remove fully sold entries
        for i in reversed(entries_to_remove):
            del crops_list[i]
        
        # Emit sale event
        sold_quantity = quantity - remaining_to_sell
        if sold_quantity > 0:
            remaining_count = self.get_crop_count(crop_type)
            
            self.event_system.emit('crops_sold', {
                'crop_type': crop_type,
                'quantity_sold': sold_quantity,
                'price_per_unit': price_per_unit,
                'total_revenue': total_revenue,
                'remaining_inventory': remaining_count
            })
            
            # Emit inventory updated event for UI
            self.event_system.emit('inventory_updated', {
                'crop_type': crop_type,
                'quantity_sold': sold_quantity,
                'total_quantity': remaining_count,
                'storage_used': self.current_storage,
                'storage_capacity': self.storage_capacity
            })
            
            print(f"Sold {sold_quantity} {crop_type} for ${total_revenue:.2f}")
        
        return total_revenue
    
    def get_crop_count(self, crop_type: str) -> int:
        """Get total quantity of a specific crop type"""
        if crop_type not in self.crops:
            return 0
        
        return sum(entry.quantity for entry in self.crops[crop_type])
    
    def get_total_storage_used(self) -> int:
        """Get total storage space used"""
        return self.current_storage
    
    def get_storage_capacity(self) -> int:
        """Get total storage capacity"""
        return self.storage_capacity
    
    def get_storage_percentage(self) -> float:
        """Get storage usage as percentage"""
        if self.storage_capacity <= 0:
            return 100.0
        return (self.current_storage / self.storage_capacity) * 100.0
    
    def get_inventory_summary(self) -> Dict:
        """Get complete inventory status"""
        summary = {
            'total_storage_used': self.current_storage,
            'storage_capacity': self.storage_capacity,
            'storage_percentage': self.get_storage_percentage(),
            'crops': {}
        }
        
        for crop_type in self.crops:
            crop_count = self.get_crop_count(crop_type)
            if crop_count > 0:
                # Calculate average quality
                total_quality = sum(entry.quantity * entry.quality 
                                  for entry in self.crops[crop_type])
                avg_quality = total_quality / crop_count if crop_count > 0 else 0
                
                summary['crops'][crop_type] = {
                    'quantity': crop_count,
                    'average_quality': avg_quality,
                    'entries': len(self.crops[crop_type])
                }
        
        return summary
    
    def can_store_crop(self, crop_type: str, quantity: int) -> bool:
        """Check if inventory has space for crops"""
        return (self.current_storage + quantity) <= self.storage_capacity
    
    def upgrade_storage(self, additional_capacity: int):
        """Upgrade storage capacity (for future building system)"""
        old_capacity = self.storage_capacity
        self.storage_capacity += additional_capacity
        
        self.event_system.emit('storage_upgraded', {
            'old_capacity': old_capacity,
            'new_capacity': self.storage_capacity,
            'additional_capacity': additional_capacity
        })
        
        print(f"Storage upgraded: {old_capacity} -> {self.storage_capacity}")
    
    def _handle_crop_harvest(self, event_data):
        """Handle crop harvest events"""
        crop_type = event_data.get('crop_type', 'corn')
        quantity = event_data.get('quantity', 0)
        quality = event_data.get('quality', 1.0)
        harvest_day = event_data.get('day', 1)
        
        if quantity > 0:
            success = self.add_crop(crop_type, quantity, quality, harvest_day)
            
            if not success:
                print(f"Warning: Could not store all harvested {crop_type} - storage full!")
    
    def _handle_sell_request(self, event_data):
        """Handle manual sell requests from UI"""
        crop_type = event_data.get('crop_type', 'corn')
        quantity = event_data.get('quantity', 0)
        price_per_unit = event_data.get('price_per_unit', 0)
        
        if quantity > 0 and price_per_unit > 0:
            revenue = self.sell_crop(crop_type, quantity, price_per_unit)
            
            # Forward revenue to economy manager
            if revenue > 0:
                self.event_system.emit('inventory_sale_completed', {
                    'crop_type': crop_type,
                    'quantity': quantity,
                    'revenue': revenue
                })
    
    def update(self, dt: float):
        """Update inventory (future: handle spoilage, etc.)"""
        # Future implementation: crop spoilage over time
        pass
    
    def get_crop_entries(self, crop_type: str) -> List[CropEntry]:
        """Get all crop entries for a type (for advanced UI)"""
        return self.crops.get(crop_type, []).copy()
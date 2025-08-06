"""
Data models for table information.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class TableCoordinate:
    """Data model for a table coordinate."""
    id: int
    page: int
    x1: float
    y1: float
    x2: float
    y2: float
    width: float = field(init=False)
    height: float = field(init=False)
    user_created: bool = False
    accuracy: float = 0.0
    whitespace: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Calculate derived values after initialization."""
        self.width = abs(self.x2 - self.x1)
        self.height = abs(self.y2 - self.y1)
        
        # Ensure coordinates are in correct order
        if self.x1 > self.x2:
            self.x1, self.x2 = self.x2, self.x1
        if self.y1 > self.y2:
            self.y1, self.y2 = self.y2, self.y1
        
        # Recalculate after potential swapping
        self.width = self.x2 - self.x1
        self.height = self.y2 - self.y1
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'id': self.id,
            'page': self.page,
            'x1': self.x1,
            'y1': self.y1,
            'x2': self.x2,
            'y2': self.y2,
            'width': self.width,
            'height': self.height,
            'user_created': self.user_created,
            'accuracy': self.accuracy,
            'whitespace': self.whitespace,
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TableCoordinate':
        """Create instance from dictionary."""
        # Parse datetime strings if present
        created_at = datetime.now()
        modified_at = datetime.now()
        
        if 'created_at' in data:
            try:
                created_at = datetime.fromisoformat(data['created_at'])
            except:
                pass
        
        if 'modified_at' in data:
            try:
                modified_at = datetime.fromisoformat(data['modified_at'])
            except:
                pass
        
        return cls(
            id=data['id'],
            page=data['page'],
            x1=data['x1'],
            y1=data['y1'],
            x2=data['x2'],
            y2=data['y2'],
            user_created=data.get('user_created', False),
            accuracy=data.get('accuracy', 0.0),
            whitespace=data.get('whitespace', 0.0),
            created_at=created_at,
            modified_at=modified_at
        )
    
    def get_bbox(self) -> tuple:
        """Get bounding box as tuple."""
        return (self.x1, self.y1, self.x2, self.y2)
    
    def get_area(self) -> float:
        """Get the area of the table."""
        return self.width * self.height
    
    def contains_point(self, x: float, y: float) -> bool:
        """Check if a point is within this table region."""
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2
    
    def overlaps_with(self, other: 'TableCoordinate') -> bool:
        """Check if this table overlaps with another table."""
        return not (self.x2 < other.x1 or self.x1 > other.x2 or 
                   self.y2 < other.y1 or self.y1 > other.y2)
    
    def update_position(self, x1: float, y1: float, x2: float, y2: float):
        """Update the position and recalculate derived values."""
        self.x1 = min(x1, x2)
        self.y1 = min(y1, y2)
        self.x2 = max(x1, x2)
        self.y2 = max(y1, y2)
        self.width = self.x2 - self.x1
        self.height = self.y2 - self.y1
        self.modified_at = datetime.now()


@dataclass
class PDFDocument:
    """Data model for PDF document information."""
    file_path: str
    page_count: int
    file_size: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    last_processed: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'file_path': self.file_path,
            'page_count': self.page_count,
            'file_size': self.file_size,
            'created_at': self.created_at.isoformat(),
            'last_processed': self.last_processed.isoformat() if self.last_processed else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PDFDocument':
        """Create instance from dictionary."""
        created_at = datetime.now()
        last_processed = None
        
        if 'created_at' in data:
            try:
                created_at = datetime.fromisoformat(data['created_at'])
            except:
                pass
        
        if 'last_processed' in data and data['last_processed']:
            try:
                last_processed = datetime.fromisoformat(data['last_processed'])
            except:
                pass
        
        return cls(
            file_path=data['file_path'],
            page_count=data['page_count'],
            file_size=data.get('file_size', 0),
            created_at=created_at,
            last_processed=last_processed
        )


@dataclass
class TableExtractionSession:
    """Data model for a table extraction session."""
    pdf_document: PDFDocument
    coordinates: List[TableCoordinate] = field(default_factory=list)
    session_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    extraction_settings: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        """Generate session ID if not provided."""
        if not self.session_id:
            self.session_id = f"session_{self.created_at.strftime('%Y%m%d_%H%M%S')}"
    
    def add_coordinate(self, coordinate: TableCoordinate):
        """Add a coordinate to the session."""
        self.coordinates.append(coordinate)
        self.modified_at = datetime.now()
    
    def remove_coordinate(self, coord_id: int) -> bool:
        """Remove a coordinate by ID."""
        for i, coord in enumerate(self.coordinates):
            if coord.id == coord_id:
                del self.coordinates[i]
                self.modified_at = datetime.now()
                return True
        return False
    
    def get_coordinate(self, coord_id: int) -> Optional[TableCoordinate]:
        """Get a coordinate by ID."""
        for coord in self.coordinates:
            if coord.id == coord_id:
                return coord
        return None
    
    def get_coordinates_for_page(self, page: int) -> List[TableCoordinate]:
        """Get all coordinates for a specific page."""
        return [coord for coord in self.coordinates if coord.page == page]
    
    def get_statistics(self) -> Dict:
        """Get session statistics."""
        if not self.coordinates:
            return {
                'total_tables': 0,
                'pages_with_tables': 0,
                'user_created': 0,
                'auto_detected': 0,
                'avg_accuracy': 0,
                'total_area': 0
            }
        
        pages = set(coord.page for coord in self.coordinates)
        user_created = sum(1 for coord in self.coordinates if coord.user_created)
        auto_detected = len(self.coordinates) - user_created
        
        accuracies = [coord.accuracy for coord in self.coordinates if not coord.user_created]
        avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0
        
        total_area = sum(coord.get_area() for coord in self.coordinates)
        
        return {
            'total_tables': len(self.coordinates),
            'pages_with_tables': len(pages),
            'user_created': user_created,
            'auto_detected': auto_detected,
            'avg_accuracy': avg_accuracy,
            'total_area': total_area
        }
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'session_id': self.session_id,
            'pdf_document': self.pdf_document.to_dict(),
            'coordinates': [coord.to_dict() for coord in self.coordinates],
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat(),
            'extraction_settings': self.extraction_settings
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TableExtractionSession':
        """Create instance from dictionary."""
        pdf_doc = PDFDocument.from_dict(data['pdf_document'])
        coordinates = [TableCoordinate.from_dict(coord_data) 
                      for coord_data in data.get('coordinates', [])]
        
        created_at = datetime.now()
        modified_at = datetime.now()
        
        if 'created_at' in data:
            try:
                created_at = datetime.fromisoformat(data['created_at'])
            except:
                pass
        
        if 'modified_at' in data:
            try:
                modified_at = datetime.fromisoformat(data['modified_at'])
            except:
                pass
        
        return cls(
            session_id=data.get('session_id', ''),
            pdf_document=pdf_doc,
            coordinates=coordinates,
            created_at=created_at,
            modified_at=modified_at,
            extraction_settings=data.get('extraction_settings', {})
        )

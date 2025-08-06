"""
Storage module for saving and loading coordinates and session data.
"""
import json
import os
from typing import List, Dict, Optional
from datetime import datetime
from .models import TableCoordinate, PDFDocument, TableExtractionSession


class StorageManager:
    """Handles saving and loading of table extraction data."""
    
    def __init__(self, base_dir: str = "table_vision_data"):
        self.base_dir = base_dir
        self.sessions_dir = os.path.join(base_dir, "sessions")
        self.coordinates_dir = os.path.join(base_dir, "coordinates")
        self.exports_dir = os.path.join(base_dir, "exports")
        
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure storage directories exist."""
        for directory in [self.base_dir, self.sessions_dir, 
                         self.coordinates_dir, self.exports_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def save_session(self, session: TableExtractionSession) -> str:
        """
        Save a complete extraction session.
        
        Args:
            session: TableExtractionSession to save
            
        Returns:
            Path to the saved session file
        """
        filename = f"{session.session_id}.json"
        filepath = os.path.join(self.sessions_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
            
            return filepath
            
        except Exception as e:
            print(f"Error saving session: {e}")
            return ""
    
    def load_session(self, session_id: str) -> Optional[TableExtractionSession]:
        """
        Load an extraction session by ID.
        
        Args:
            session_id: ID of the session to load
            
        Returns:
            TableExtractionSession or None if not found/error
        """
        filename = f"{session_id}.json"
        filepath = os.path.join(self.sessions_dir, filename)
        
        if not os.path.exists(filepath):
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return TableExtractionSession.from_dict(data)
            
        except Exception as e:
            print(f"Error loading session: {e}")
            return None
    
    def list_sessions(self) -> List[Dict]:
        """
        List all available sessions with metadata.
        
        Returns:
            List of session metadata dictionaries
        """
        sessions = []
        
        if not os.path.exists(self.sessions_dir):
            return sessions
        
        for filename in os.listdir(self.sessions_dir):
            if filename.endswith('.json'):
                session_id = filename[:-5]  # Remove .json extension
                filepath = os.path.join(self.sessions_dir, filename)
                
                try:
                    # Get file stats
                    stat = os.stat(filepath)
                    
                    # Try to read basic info from file
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    sessions.append({
                        'session_id': session_id,
                        'pdf_path': data.get('pdf_document', {}).get('file_path', ''),
                        'total_tables': len(data.get('coordinates', [])),
                        'created_at': data.get('created_at', ''),
                        'modified_at': data.get('modified_at', ''),
                        'file_size': stat.st_size,
                        'file_modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                    
                except Exception as e:
                    print(f"Error reading session {session_id}: {e}")
        
        # Sort by modified time (newest first)
        sessions.sort(key=lambda x: x.get('file_modified', ''), reverse=True)
        return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session file.
        
        Args:
            session_id: ID of the session to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        filename = f"{session_id}.json"
        filepath = os.path.join(self.sessions_dir, filename)
        
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
        except Exception as e:
            print(f"Error deleting session: {e}")
        
        return False
    
    def save_coordinates_csv(self, coordinates: List[TableCoordinate], 
                           output_path: str) -> bool:
        """
        Export coordinates to CSV format.
        
        Args:
            coordinates: List of TableCoordinate objects
            output_path: Path to save CSV file
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            import csv
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow([
                    'id', 'page', 'x1', 'y1', 'x2', 'y2', 'width', 'height',
                    'user_created', 'accuracy', 'whitespace', 'created_at', 'modified_at'
                ])
                
                # Write data
                for coord in coordinates:
                    writer.writerow([
                        coord.id, coord.page, coord.x1, coord.y1, coord.x2, coord.y2,
                        coord.width, coord.height, coord.user_created, coord.accuracy,
                        coord.whitespace, coord.created_at.isoformat(), 
                        coord.modified_at.isoformat()
                    ])
            
            return True
            
        except Exception as e:
            print(f"Error saving coordinates to CSV: {e}")
            return False
    
    def load_coordinates_csv(self, csv_path: str) -> List[TableCoordinate]:
        """
        Load coordinates from CSV format.
        
        Args:
            csv_path: Path to CSV file
            
        Returns:
            List of TableCoordinate objects
        """
        coordinates = []
        
        try:
            import csv
            
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    # Convert string values to appropriate types
                    coord_data = {
                        'id': int(row['id']),
                        'page': int(row['page']),
                        'x1': float(row['x1']),
                        'y1': float(row['y1']),
                        'x2': float(row['x2']),
                        'y2': float(row['y2']),
                        'user_created': row['user_created'].lower() == 'true',
                        'accuracy': float(row['accuracy']),
                        'whitespace': float(row['whitespace']),
                        'created_at': row['created_at'],
                        'modified_at': row['modified_at']
                    }
                    
                    coordinates.append(TableCoordinate.from_dict(coord_data))
            
            return coordinates
            
        except Exception as e:
            print(f"Error loading coordinates from CSV: {e}")
            return []
    
    def save_coordinates_json(self, coordinates: List[TableCoordinate], 
                            output_path: str) -> bool:
        """
        Save coordinates to JSON format.
        
        Args:
            coordinates: List of TableCoordinate objects
            output_path: Path to save JSON file
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            data = {
                'coordinates': [coord.to_dict() for coord in coordinates],
                'exported_at': datetime.now().isoformat(),
                'total_count': len(coordinates)
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error saving coordinates to JSON: {e}")
            return False
    
    def load_coordinates_json(self, json_path: str) -> List[TableCoordinate]:
        """
        Load coordinates from JSON format.
        
        Args:
            json_path: Path to JSON file
            
        Returns:
            List of TableCoordinate objects
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            coordinates = []
            for coord_data in data.get('coordinates', []):
                coordinates.append(TableCoordinate.from_dict(coord_data))
            
            return coordinates
            
        except Exception as e:
            print(f"Error loading coordinates from JSON: {e}")
            return []
    
    def get_exports_directory(self) -> str:
        """Get the exports directory path."""
        return self.exports_dir
    
    def create_export_directory(self, session_id: str) -> str:
        """
        Create a directory for exporting session data.
        
        Args:
            session_id: Session ID to create directory for
            
        Returns:
            Path to the created directory
        """
        export_dir = os.path.join(self.exports_dir, session_id)
        os.makedirs(export_dir, exist_ok=True)
        return export_dir
    
    def cleanup_old_sessions(self, days: int = 30) -> int:
        """
        Clean up session files older than specified days.
        
        Args:
            days: Number of days to keep sessions
            
        Returns:
            Number of files deleted
        """
        if not os.path.exists(self.sessions_dir):
            return 0
        
        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
        deleted_count = 0
        
        for filename in os.listdir(self.sessions_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.sessions_dir, filename)
                
                try:
                    stat = os.stat(filepath)
                    if stat.st_mtime < cutoff_time:
                        os.remove(filepath)
                        deleted_count += 1
                except Exception as e:
                    print(f"Error deleting old session {filename}: {e}")
        
        return deleted_count
    
    def get_storage_stats(self) -> Dict:
        """
        Get storage usage statistics.
        
        Returns:
            Dictionary with storage statistics
        """
        stats = {
            'total_sessions': 0,
            'total_size_bytes': 0,
            'oldest_session': None,
            'newest_session': None
        }
        
        if not os.path.exists(self.sessions_dir):
            return stats
        
        session_files = []
        total_size = 0
        
        for filename in os.listdir(self.sessions_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.sessions_dir, filename)
                
                try:
                    stat = os.stat(filepath)
                    total_size += stat.st_size
                    session_files.append((filename, stat.st_mtime))
                except:
                    continue
        
        if session_files:
            session_files.sort(key=lambda x: x[1])  # Sort by modification time
            
            stats['total_sessions'] = len(session_files)
            stats['total_size_bytes'] = total_size
            stats['oldest_session'] = session_files[0][0][:-5]  # Remove .json
            stats['newest_session'] = session_files[-1][0][:-5]  # Remove .json
        
        return stats

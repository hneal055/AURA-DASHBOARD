#!/usr/bin/env python3
"""
AURA SCREENPLAY PARSER v2.0 - Enhanced Fountain Format Parser
Comprehensive parsing with full Fountain spec support
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class Character:
    name: str
    dialogue_lines: List[str] = field(default_factory=list)
    scene_appearances: List[int] = field(default_factory=list)
    line_count: int = 0

@dataclass
class Scene:
    number: int
    heading: str
    location: str
    time_of_day: str
    interior_exterior: str
    characters: List[str] = field(default_factory=list)
    dialogue_count: int = 0
    action_lines: List[str] = field(default_factory=list)
    
@dataclass
class ScreenplayMetadata:
    title: Optional[str] = None
    author: Optional[str] = None
    credit: Optional[str] = None
    source: Optional[str] = None
    draft_date: Optional[str] = None
    contact: Optional[str] = None

class FountainParser:
    """Enhanced Fountain format parser with full spec support"""
    
    # Fountain format regex patterns
    PATTERNS = {
        'scene_heading': r'^(INT|EXT|EST|INT\./EXT|INT/EXT|I/E)[\.\s]+',
        'character': r'^([A-Z][A-Z\s\d\(\)]+)$',
        'dialogue': r'^(?!\s*$).+',
        'action': r'^(?!\s*$).+',
        'transition': r'^(CUT TO:|FADE TO:|DISSOLVE TO:|FADE OUT\.|FADE IN:|TO:)$',
        'centered': r'^\s*>\s*(.+?)\s*<\s*$',
        'page_break': r'^={3,}$',
        'section': r'^(#+)\s*(.+)$',
        'synopsis': r'^=\s*(.+)$',
        'note': r'\[\[(.+?)\]\]',
        'boneyard': r'/\*(.+?)\*/',
        'lyric': r'^~(.+)$'
    }
    
    def __init__(self):
        self.metadata = ScreenplayMetadata()
        self.scenes: List[Scene] = []
        self.characters: Dict[str, Character] = {}
        self.current_scene: Optional[Scene] = None
        self.current_character: Optional[str] = None
        
    def parse(self, content: str) -> Dict:
        """Main parsing method"""
        lines = content.split('\n')
        
        # First pass: extract metadata
        metadata_end = self._extract_metadata(lines)
        
        # Second pass: parse screenplay content
        self._parse_content(lines[metadata_end:])
        
        # Calculate statistics
        stats = self._calculate_statistics()
        
        return {
            'metadata': {
                'title': self.metadata.title,
                'author': self.metadata.author,
                'credit': self.metadata.credit,
                'draft_date': self.metadata.draft_date
            },
            'scenes': [self._scene_to_dict(scene) for scene in self.scenes],
            'characters': [self._character_to_dict(char) for char in self.characters.values()],
            'statistics': stats,
            'structure': self._analyze_structure()
        }
    
    def _extract_metadata(self, lines: List[str]) -> int:
        """Extract title page metadata"""
        metadata_pattern = r'^([A-Za-z\s]+):\s*(.+)$'
        line_index = 0
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            if not line:
                continue
                
            match = re.match(metadata_pattern, line)
            if match:
                key, value = match.groups()
                key = key.lower().replace(' ', '_')
                
                if key == 'title':
                    self.metadata.title = value
                elif key == 'author' or key == 'authors':
                    self.metadata.author = value
                elif key == 'credit':
                    self.metadata.credit = value
                elif key == 'source':
                    self.metadata.source = value
                elif key in ['draft_date', 'date']:
                    self.metadata.draft_date = value
                elif key == 'contact':
                    self.metadata.contact = value
                    
                line_index = i + 1
            else:
                # Metadata section ends at first non-metadata line
                if line and not line.startswith('\t'):
                    break
        
        return line_index
    
    def _parse_content(self, lines: List[str]):
        """Parse screenplay content"""
        i = 0
        
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # Skip empty lines
            if not stripped:
                i += 1
                continue
            
            # Check for scene heading
            if self._is_scene_heading(stripped):
                self._parse_scene_heading(stripped)
                self.current_character = None
                
            # Check for character name
            elif self._is_character_name(stripped):
                self.current_character = self._normalize_character_name(stripped)
                if self.current_character not in self.characters:
                    self.characters[self.current_character] = Character(
                        name=self.current_character
                    )
                if self.current_scene:
                    if self.current_character not in self.current_scene.characters:
                        self.current_scene.characters.append(self.current_character)
                    self.characters[self.current_character].scene_appearances.append(
                        self.current_scene.number
                    )
                
            # Check for dialogue
            elif self.current_character and stripped and not self._is_parenthetical(stripped):
                self.characters[self.current_character].dialogue_lines.append(stripped)
                self.characters[self.current_character].line_count += 1
                if self.current_scene:
                    self.current_scene.dialogue_count += 1
                
            # Action line
            elif self.current_scene and not self._is_transition(stripped):
                self.current_scene.action_lines.append(stripped)
                
            i += 1
    
    def _is_scene_heading(self, line: str) -> bool:
        """Check if line is a scene heading"""
        return bool(re.match(self.PATTERNS['scene_heading'], line, re.IGNORECASE))
    
    def _is_character_name(self, line: str) -> bool:
        """Check if line is a character name"""
        # Must be all caps, not a scene heading, reasonable length
        if not line.isupper():
            return False
        if self._is_scene_heading(line):
            return False
        if len(line) < 2 or len(line) > 50:
            return False
        return True
    
    def _is_parenthetical(self, line: str) -> bool:
        """Check if line is a parenthetical"""
        return line.startswith('(') and line.endswith(')')
    
    def _is_transition(self, line: str) -> bool:
        """Check if line is a transition"""
        return bool(re.match(self.PATTERNS['transition'], line, re.IGNORECASE))
    
    def _normalize_character_name(self, name: str) -> str:
        """Normalize character name (remove extensions like (V.O.))"""
        # Remove parenthetical extensions
        name = re.sub(r'\s*\([^\)]+\)', '', name)
        return name.strip()
    
    def _parse_scene_heading(self, heading: str):
        """Parse scene heading and extract details"""
        scene_number = len(self.scenes) + 1
        
        # Extract INT/EXT
        int_ext_match = re.match(r'^(INT|EXT|EST|INT\./EXT|INT/EXT|I/E)', heading, re.IGNORECASE)
        interior_exterior = int_ext_match.group(1) if int_ext_match else 'UNKNOWN'
        
        # Extract location and time
        parts = heading.split('-')
        location = parts[0].strip() if len(parts) > 0 else heading
        time_of_day = parts[-1].strip() if len(parts) > 1 else 'UNKNOWN'
        
        scene = Scene(
            number=scene_number,
            heading=heading,
            location=location,
            time_of_day=time_of_day,
            interior_exterior=interior_exterior
        )
        
        if self.current_scene:
            self.scenes.append(self.current_scene)
        
        self.current_scene = scene
    
    def _calculate_statistics(self) -> Dict:
        """Calculate screenplay statistics"""
        total_dialogue_lines = sum(char.line_count for char in self.characters.values())
        total_scenes = len(self.scenes)
        
        return {
            'scene_count': total_scenes,
            'character_count': len(self.characters),
            'dialogue_lines': total_dialogue_lines,
            'average_scene_length': total_dialogue_lines / total_scenes if total_scenes > 0 else 0,
            'interior_scenes': len([s for s in self.scenes if 'INT' in s.interior_exterior]),
            'exterior_scenes': len([s for s in self.scenes if 'EXT' in s.interior_exterior])
        }
    
    def _analyze_structure(self) -> Dict:
        """Analyze three-act structure"""
        total_scenes = len(self.scenes)
        
        act1_end = int(total_scenes * 0.25)
        act2_end = int(total_scenes * 0.75)
        
        return {
            'act_1': {'start': 1, 'end': act1_end, 'scenes': act1_end},
            'act_2': {'start': act1_end + 1, 'end': act2_end, 'scenes': act2_end - act1_end},
            'act_3': {'start': act2_end + 1, 'end': total_scenes, 'scenes': total_scenes - act2_end}
        }
    
    def _scene_to_dict(self, scene: Scene) -> Dict:
        """Convert scene to dictionary"""
        return {
            'number': scene.number,
            'heading': scene.heading,
            'location': scene.location,
            'time': scene.time_of_day,
            'type': scene.interior_exterior,
            'characters': scene.characters,
            'dialogue_count': scene.dialogue_count,
            'action_lines': len(scene.action_lines)
        }
    
    def _character_to_dict(self, character: Character) -> Dict:
        """Convert character to dictionary"""
        return {
            'name': character.name,
            'line_count': character.line_count,
            'scene_count': len(character.scene_appearances),
            'scenes': character.scene_appearances
        }

# Usage example
if __name__ == '__main__':
    sample_fountain = """
Title: SAMPLE SCREENPLAY
Author: John Doe
Draft Date: November 26, 2024

INT. COFFEE SHOP - DAY

ALICE sits at a corner table, nursing a latte.

BOB enters, looking frazzled.

BOB
Have you seen my keys?

ALICE
(smiling)
Again? That's the third time this week.

BOB
I know, I know. I'm a disaster.

EXT. CITY STREET - DAY

Bob and Alice walk together.
"""
    
    parser = FountainParser()
    result = parser.parse(sample_fountain)
    
    print("Parsed Screenplay:")
    print(f"Title: {result['metadata']['title']}")
    print(f"Scenes: {result['statistics']['scene_count']}")
    print(f"Characters: {result['statistics']['character_count']}")
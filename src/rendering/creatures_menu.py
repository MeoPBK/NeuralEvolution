"""
Creatures Menu module for the simulation.
This module handles the creatures menu that shows saved creatures with filtering options.
"""

import pygame
import json
import os
from datetime import datetime


class CreatureSaver:
    """Manages saving and loading of creatures."""
    
    def __init__(self):
        self.saved_creatures = {}
        self.save_directory = "saves/creatures"
        
        # Create save directory if it doesn't exist
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)
    
    def save_creature(self, agent, name=""):
        """Save a creature's data."""
        creature_data = {
            'id': agent.id,
            'name': name,
            'generation': agent.generation,
            'species_id': agent.species_id,
            'alive': agent.alive,
            'age': agent.age,
            'energy': agent.energy,
            'hydration': agent.hydration,
            'size': agent.size,
            'speed': agent.speed,
            'aggression': agent.aggression,
            'efficiency': agent.efficiency,
            'vision_range': agent.vision_range,
            'max_age': agent.max_age,
            'virus_resistance': agent.virus_resistance,
            'armor': agent.armor,
            'agility': agent.agility,
            'diet_type': agent.diet_type,
            'habitat_preference': agent.habitat_preference,
            'offspring_count': agent.offspring_count,
            'total_mutations': agent.total_mutations,
            'timestamp': datetime.now().isoformat(),
            'phenotype': dict(agent.phenotype),
            'shape_type': agent.shape_type
        }
        
        filename = f"{self.save_directory}/creature_{agent.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(creature_data, f, indent=2)
        
        self.saved_creatures[agent.id] = creature_data
        return filename
    
    def load_saved_creatures(self):
        """Load all saved creatures from the save directory."""
        self.saved_creatures = {}
        if not os.path.exists(self.save_directory):
            return []
        
        creature_files = [f for f in os.listdir(self.save_directory) if f.endswith('.json')]
        creatures = []
        
        for filename in creature_files:
            filepath = os.path.join(self.save_directory, filename)
            try:
                with open(filepath, 'r') as f:
                    creature_data = json.load(f)
                    creatures.append(creature_data)
                    self.saved_creatures[creature_data['id']] = creature_data
            except Exception as e:
                print(f"Error loading creature file {filename}: {e}")
        
        # Sort by timestamp (newest first)
        creatures.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return creatures


class CreaturesMenu:
    """Creatures menu that displays saved creatures with filtering options."""
    
    def __init__(self, settings):
        self.settings = settings
        self.visible = False
        self.creature_saver = CreatureSaver()
        
        # Window dimensions
        self.window_width = 1200
        self.window_height = 800
        
        # Filtering options
        self.filter_alive = None  # None = all, True = alive, False = dead
        self.filter_species = None
        self.filter_generation_min = 0
        self.filter_generation_max = float('inf')
        self.search_term = ""
        
        # Pagination
        self.page_size = 15
        self.current_page = 0
        
        # UI Elements
        self.scroll_offset = 0
        self.max_scroll = 0
        self.selected_creature = None
        
        # Fonts
        self.font_tiny = pygame.font.SysFont('monospace', 9)
        self.font_small = pygame.font.SysFont('monospace', 11)
        self.font_medium = pygame.font.SysFont('monospace', 13)
        self.font_large = pygame.font.SysFont('monospace', 15)
        self.font_title = pygame.font.SysFont('monospace', 18, bold=True)
        
        # UI Colors
        self.bg_color = (35, 38, 45)
        self.panel_color = (28, 31, 38)
        self.card_color = (42, 45, 55)
        self.border_color = (70, 75, 85)
        self.text_color = (220, 220, 225)
        self.header_color = (180, 185, 200)
        self.accent_color = (100, 150, 255)
        self.alive_color = (100, 200, 100)
        self.dead_color = (200, 100, 100)
    
    def toggle_visibility(self):
        """Toggle the visibility of the creatures menu."""
        self.visible = not self.visible
        if self.visible:
            # Reload creatures when menu is opened
            self.creature_saver.load_saved_creatures()
    
    def draw(self, screen):
        """Draw the creatures menu."""
        if not self.visible:
            return
        
        # Center the window on the screen
        screen_width, screen_height = screen.get_size()
        window_x = (screen_width - self.window_width) // 2
        window_y = (screen_height - self.window_height) // 2
        
        # Draw window background with shadow
        pygame.draw.rect(screen, (20, 20, 25), (window_x + 5, window_y + 5, self.window_width, self.window_height))
        pygame.draw.rect(screen, self.bg_color, (window_x, window_y, self.window_width, self.window_height))
        pygame.draw.rect(screen, self.border_color, (window_x, window_y, self.window_width, self.window_height), 2)
        
        # Header bar
        header_height = 80
        pygame.draw.rect(screen, self.panel_color, (window_x, window_y, self.window_width, header_height))
        pygame.draw.line(screen, self.border_color, (window_x, window_y + header_height),
                        (window_x + self.window_width, window_y + header_height), 1)
        
        # Title
        title = self.font_title.render("Saved Creatures", True, self.accent_color)
        screen.blit(title, (window_x + 15, window_y + 10))
        
        # Subtitle with count
        all_creatures = self.creature_saver.load_saved_creatures()
        filtered_creatures = self._filter_creatures(all_creatures)
        subtitle = self.font_medium.render(f"Total: {len(all_creatures)} | Filtered: {len(filtered_creatures)}", True, self.text_color)
        screen.blit(subtitle, (window_x + 15, window_y + 35))
        
        # Close hint
        close_hint = self.font_small.render("[C] to close", True, (150, 150, 160))
        screen.blit(close_hint, (window_x + self.window_width - 90, window_y + 14))
        
        # Draw filters panel
        self._draw_filters(screen, window_x, window_y + header_height + 5, self.window_width, 100)
        
        # Draw creature list
        list_y = window_y + header_height + 105
        list_height = self.window_height - header_height - 110
        self._draw_creature_list(screen, window_x, list_y, self.window_width, list_height, filtered_creatures)
    
    def _draw_filters(self, screen, x, y, width, height):
        """Draw the filter controls."""
        # Panel background
        pygame.draw.rect(screen, self.panel_color, (x, y, width, height))
        pygame.draw.rect(screen, self.border_color, (x, y, width, height), 1)
        
        # Filter labels and controls
        filter_x = x + 15
        filter_y = y + 10
        
        # Status filter (Alive/Dead/All)
        status_label = self.font_medium.render("Status:", True, self.header_color)
        screen.blit(status_label, (filter_x, filter_y))
        
        # Status buttons
        status_buttons = [
            ("All", None),
            ("Alive", True),
            ("Dead", False)
        ]
        
        btn_x = filter_x + 60
        for text, status in status_buttons:
            color = self.accent_color if self.filter_alive == status else self.text_color
            btn_text = self.font_small.render(text, True, color)
            screen.blit(btn_text, (btn_x, filter_y))
            btn_x += 60
        
        # Generation filter
        gen_label = self.font_medium.render("Gen:", True, self.header_color)
        screen.blit(gen_label, (filter_x, filter_y + 25))
        
        gen_range = self.font_small.render(f"{self.filter_generation_min}-{self.filter_generation_max}", True, self.text_color)
        screen.blit(gen_range, (filter_x + 40, filter_y + 25))
        
        # Search box
        search_label = self.font_medium.render("Search:", True, self.header_color)
        screen.blit(search_label, (filter_x + 200, filter_y))
        
        search_box = pygame.Rect(filter_x + 260, filter_y, 150, 20)
        pygame.draw.rect(screen, (50, 55, 65), search_box)
        pygame.draw.rect(screen, self.border_color, search_box, 1)
        
        search_text = self.font_small.render(self.search_term or "Name/ID...", True, self.text_color if self.search_term else (150, 150, 160))
        screen.blit(search_text, (search_box.x + 5, search_box.y + 2))
    
    def _draw_creature_list(self, screen, x, y, width, height, creatures):
        """Draw the list of creatures."""
        # Calculate pagination
        total_pages = max(1, (len(creatures) + self.page_size - 1) // self.page_size)
        start_idx = self.current_page * self.page_size
        end_idx = min(start_idx + self.page_size, len(creatures))
        page_creatures = creatures[start_idx:end_idx]
        
        # Draw list background
        pygame.draw.rect(screen, self.panel_color, (x, y, width, height))
        pygame.draw.rect(screen, self.border_color, (x, y, width, height), 1)
        
        # Draw headers
        headers_y = y + 5
        headers = [
            ("ID", 50),
            ("Name", 150),
            ("Status", 80),
            ("Species", 100),
            ("Gen", 60),
            ("Age", 60),
            ("Size", 60),
            ("Speed", 60),
            ("Aggr", 60),
            ("Mut", 60)
        ]
        
        header_x = x + 10
        for header, h_width in headers:
            header_text = self.font_small.render(header, True, self.header_color)
            screen.blit(header_text, (header_x, headers_y))
            header_x += h_width
        
        # Draw creature rows
        row_y = y + 30
        row_height = 25
        
        for i, creature in enumerate(page_creatures):
            # Alternate row colors
            row_bg_color = self.card_color if i % 2 == 0 else (45, 48, 58)
            pygame.draw.rect(screen, row_bg_color, (x, row_y + i * row_height, width, row_height))
            
            # Draw creature data
            data_x = x + 10
            data = [
                str(creature['id']),
                creature['name'] or f"Creature {creature['id']}",
                "✓" if creature['alive'] else "✗",
                f"#{creature['species_id']}",
                str(creature['generation']),
                f"{creature['age']:.1f}",
                f"{creature['size']:.2f}",
                f"{creature['speed']:.2f}",
                f"{creature['aggression']:.2f}",
                str(creature['total_mutations'])
            ]
            
            for j, (value, _) in enumerate(headers):
                if j < len(data):
                    color = self.alive_color if j == 2 and creature['alive'] else self.dead_color if j == 2 and not creature['alive'] else self.text_color
                    text = self.font_small.render(data[j], True, color)
                    screen.blit(text, (data_x, row_y + i * row_height + 5))
                    data_x += headers[j][1]
        
        # Draw pagination controls
        pagination_y = y + height - 30
        page_text = self.font_small.render(f"Page {self.current_page + 1} of {total_pages}", True, self.text_color)
        screen.blit(page_text, (x + 20, pagination_y))
        
        # Page navigation buttons
        if self.current_page > 0:
            prev_btn = pygame.Rect(x + width - 120, pagination_y, 50, 20)
            pygame.draw.rect(screen, self.panel_color, prev_btn)
            pygame.draw.rect(screen, self.border_color, prev_btn, 1)
            prev_text = self.font_small.render("Prev", True, self.text_color)
            screen.blit(prev_text, (prev_btn.centerx - prev_text.get_width() // 2, 
                                   prev_btn.centery - prev_text.get_height() // 2))
        
        if self.current_page < total_pages - 1:
            next_btn = pygame.Rect(x + width - 60, pagination_y, 50, 20)
            pygame.draw.rect(screen, self.panel_color, next_btn)
            pygame.draw.rect(screen, self.border_color, next_btn, 1)
            next_text = self.font_small.render("Next", True, self.text_color)
            screen.blit(next_text, (next_btn.centerx - next_text.get_width() // 2, 
                                   next_btn.centery - next_text.get_height() // 2))
    
    def _filter_creatures(self, creatures):
        """Filter creatures based on current filter settings."""
        filtered = creatures
        
        # Filter by alive/dead status
        if self.filter_alive is not None:
            filtered = [c for c in filtered if c['alive'] == self.filter_alive]
        
        # Filter by generation range
        filtered = [c for c in filtered if self.filter_generation_min <= c['generation'] <= self.filter_generation_max]
        
        # Filter by search term
        if self.search_term:
            term = self.search_term.lower()
            filtered = [c for c in filtered 
                       if term in c['name'].lower() or term in str(c['id'])]
        
        return filtered
    
    def handle_click(self, pos):
        """Handle mouse clicks on the menu."""
        screen_width, screen_height = pygame.display.get_surface().get_size()
        window_x = (screen_width - self.window_width) // 2
        window_y = (screen_height - self.window_height) // 2

        # Check if click is inside the window
        if not (window_x <= pos[0] <= window_x + self.window_width and
                window_y <= pos[1] <= window_y + self.window_height):
            return False

        # Check for clicks on filter buttons
        filter_y = window_y + 85  # Header height + 5
        filter_x = window_x + 75  # After "Status:" label

        # Status filter buttons
        status_buttons = [
            ("All", None),
            ("Alive", True),
            ("Dead", False)
        ]

        for i, (text, status) in enumerate(status_buttons):
            btn_rect = pygame.Rect(filter_x + i * 60, filter_y, 50, 20)
            if btn_rect.collidepoint(pos):
                self.filter_alive = status
                self.current_page = 0  # Reset to first page when filter changes
                return True

        # Generation filter buttons (for increasing/decreasing min/max)
        gen_min_up = pygame.Rect(filter_x + 160, filter_y + 25, 20, 15)
        gen_min_down = pygame.Rect(filter_x + 160, filter_y + 40, 20, 15)
        gen_max_up = pygame.Rect(filter_x + 200, filter_y + 25, 20, 15)
        gen_max_down = pygame.Rect(filter_x + 200, filter_y + 40, 20, 15)

        if gen_min_up.collidepoint(pos):
            self.filter_generation_min = max(0, self.filter_generation_min + 1)
            self.current_page = 0
        elif gen_min_down.collidepoint(pos):
            self.filter_generation_min = max(0, self.filter_generation_min - 1)
            self.current_page = 0
        elif gen_max_up.collidepoint(pos):
            self.filter_generation_max = min(self.filter_generation_max + 1, 1000)
            self.current_page = 0
        elif gen_max_down.collidepoint(pos):
            self.filter_generation_max = max(self.filter_generation_min, self.filter_generation_max - 1)
            self.current_page = 0

        # Search box - for now just focus on it
        search_box = pygame.Rect(filter_x + 260, filter_y, 150, 20)
        if search_box.collidepoint(pos):
            # In a real implementation, we would handle text input here
            pass

        # Pagination buttons
        pagination_y = window_y + self.window_height - 25
        prev_btn = pygame.Rect(window_x + self.window_width - 120, pagination_y, 50, 20)
        next_btn = pygame.Rect(window_x + self.window_width - 60, pagination_y, 50, 20)

        if prev_btn.collidepoint(pos) and self.current_page > 0:
            self.current_page -= 1
            return True
        elif next_btn.collidepoint(pos):
            # Calculate max page based on filtered creatures
            all_creatures = self.creature_saver.load_saved_creatures()
            filtered_creatures = self._filter_creatures(all_creatures)
            max_page = max(0, (len(filtered_creatures) + self.page_size - 1) // self.page_size - 1)
            if self.current_page < max_page:
                self.current_page += 1
                return True

        return True
    
    def handle_key_press(self, key):
        """Handle keyboard input."""
        if key == pygame.K_PAGEUP and self.current_page > 0:
            self.current_page -= 1
        elif key == pygame.K_PAGEDOWN:
            # Calculate max page based on filtered creatures
            all_creatures = self.creature_saver.load_saved_creatures()
            filtered_creatures = self._filter_creatures(all_creatures)
            max_page = max(0, (len(filtered_creatures) + self.page_size - 1) // self.page_size - 1)
            if self.current_page < max_page:
                self.current_page += 1
        elif key == pygame.K_HOME:
            self.current_page = 0
        elif key == pygame.K_END:
            all_creatures = self.creature_saver.load_saved_creatures()
            filtered_creatures = self._filter_creatures(all_creatures)
            self.current_page = max(0, (len(filtered_creatures) + self.page_size - 1) // self.page_size - 1)
    
    def handle_scroll(self, direction):
        """Handle mouse wheel scrolling."""
        self.scroll_offset += direction * 30
        self.scroll_offset = max(0, min(self.max_scroll, self.scroll_offset))
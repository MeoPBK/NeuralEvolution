"""
Statistics Visualization module for the simulation.
Enhanced with comprehensive graphs, per-species tracking, and detailed analysis.
"""

import pygame
import math
from collections import defaultdict


class StatsVisualization:
    """Enhanced statistics visualization with comprehensive graphs and analysis."""

    def __init__(self, world, stats_collector=None):
        self.world = world
        self.stats_collector = stats_collector
        self.visible = False

        # Fonts
        self.font_tiny = pygame.font.SysFont('monospace', 9)
        self.font_small = pygame.font.SysFont('monospace', 11)
        self.font_medium = pygame.font.SysFont('monospace', 13)
        self.font_large = pygame.font.SysFont('monospace', 15)
        self.font_title = pygame.font.SysFont('monospace', 20, bold=True)
        self.font_header = pygame.font.SysFont('monospace', 14, bold=True)

        # Species data cache
        self.species_names = {}
        self.species_colors = {}
        self.species_shapes = ['circle', 'square', 'triangle', 'parallelogram', 'diamond', 'hexagon', 'pentagon', 'star']

        # UI Colors - Dark theme
        self.bg_color = (22, 25, 30)
        self.panel_color = (30, 34, 42)
        self.card_color = (38, 42, 52)
        self.card_header_color = (45, 50, 62)
        self.border_color = (60, 65, 78)
        self.text_color = (220, 225, 230)
        self.text_dim = (140, 145, 155)
        self.header_color = (170, 175, 190)
        self.accent_color = (90, 145, 255)
        self.accent_secondary = (255, 140, 90)

        # Graph colors
        self.graph_colors = [
            (90, 200, 250),   # Cyan
            (250, 100, 130),  # Red-pink
            (100, 220, 120),  # Green
            (255, 200, 80),   # Yellow
            (180, 130, 255),  # Purple
            (255, 150, 100),  # Orange
            (100, 200, 200),  # Teal
            (220, 180, 255),  # Lavender
        ]

        self.male_color = (100, 150, 255)
        self.female_color = (255, 120, 170)
        self.energy_color = (100, 200, 100)
        self.hydration_color = (100, 170, 255)

        # Scrolling
        self.scroll_y = 0
        self.max_scroll = 0

    def toggle_visibility(self):
        self.visible = not self.visible

    def set_stats_collector(self, stats_collector):
        self.stats_collector = stats_collector

    def get_species_name(self, species_id):
        if species_id not in self.species_names:
            names = [
                "Visconti", "Medici", "Este", "Sforza", "Gonzaga", "Farnese", "Pico", "Borgia",
                "Malatesta", "Montefeltro", "Doria", "Grimaldi", "Cybo", "Colonna", "Orsini",
                "Gentile", "Alberti", "Pazzi", "Salviati", "Rucellai", "Albizzi", "Capponi"
            ]
            self.species_names[species_id] = names[species_id % len(names)]
        return self.species_names[species_id]

    def get_species_color(self, species_id):
        if species_id not in self.species_colors:
            hue = (species_id * 137.5) % 360
            h = hue / 360.0
            s, v = 0.7, 0.95
            c = v * s
            x = c * (1 - abs((h * 6) % 2 - 1))
            m = v - c
            if h < 1/6: r, g, b = c, x, 0
            elif h < 2/6: r, g, b = x, c, 0
            elif h < 3/6: r, g, b = 0, c, x
            elif h < 4/6: r, g, b = 0, x, c
            elif h < 5/6: r, g, b = x, 0, c
            else: r, g, b = c, 0, x
            self.species_colors[species_id] = (int((r+m)*255), int((g+m)*255), int((b+m)*255))
        return self.species_colors[species_id]

    def get_species_shape(self, species_id):
        return self.species_shapes[species_id % len(self.species_shapes)]

    def draw(self, screen):
        if not self.visible or not self.world or not self.stats_collector:
            return

        sw, sh = screen.get_size()
        ww = min(1400, sw - 40)
        wh = min(950, sh - 40)
        wx = (sw - ww) // 2
        wy = (sh - wh) // 2

        # Window background with shadow
        pygame.draw.rect(screen, (10, 12, 15), (wx + 6, wy + 6, ww, wh), border_radius=8)
        pygame.draw.rect(screen, self.bg_color, (wx, wy, ww, wh), border_radius=8)
        pygame.draw.rect(screen, self.border_color, (wx, wy, ww, wh), 2, border_radius=8)

        # Header
        header_h = 50
        pygame.draw.rect(screen, self.panel_color, (wx, wy, ww, header_h), border_top_left_radius=8, border_top_right_radius=8)
        pygame.draw.line(screen, self.border_color, (wx, wy + header_h), (wx + ww, wy + header_h), 1)

        title = self.font_title.render("SIMULATION ANALYTICS", True, self.accent_color)
        screen.blit(title, (wx + 20, wy + 13))

        # Subtitle with live stats
        live_agents = [a for a in self.world.agent_list if a.alive]
        subtitle = self.font_small.render(
            f"Population: {len(live_agents)} | Species: {len(set(a.species_id for a in live_agents))} | Time: {self.stats_collector.snapshots[-1].time:.1f}s" if self.stats_collector.snapshots else "Initializing...",
            True, self.text_dim)
        screen.blit(subtitle, (wx + 20, wy + 35))

        # Close hint
        hint = self.font_small.render("[S] Close  |  Scroll: Mouse wheel", True, self.text_dim)
        screen.blit(hint, (wx + ww - hint.get_width() - 20, wy + 18))

        # Content area with clipping
        content_x = wx + 15
        content_y = wy + header_h + 10
        content_w = ww - 30
        content_h = wh - header_h - 20

        clip_rect = pygame.Rect(content_x, content_y, content_w, content_h)
        screen.set_clip(clip_rect)

        total_h = self._draw_content(screen, content_x, content_y - self.scroll_y, content_w, live_agents)

        screen.set_clip(None)

        self.max_scroll = max(0, total_h - content_h + 30)

        # Scrollbar
        if self.max_scroll > 0:
            self._draw_scrollbar(screen, wx + ww - 10, content_y, 6, content_h, total_h)

    def _draw_content(self, screen, x, y, w, live_agents):
        """Draw all content sections."""
        cy = y
        gap = 12

        # Row 1: Key metrics cards (enhanced with extra row)
        cy = self._draw_metrics_row(screen, x, cy, w, live_agents)
        cy += gap

        # Row 2: Population timeline (full width, taller for stats panel)
        cy = self._draw_card(screen, x, cy, w, 240, "POPULATION TIMELINE",
                            lambda sx, sy, sw, sh: self._draw_population_timeline(screen, sx, sy, sw, sh))
        cy += gap

        # Row 3: Species breakdown + Gender over time (taller for legends)
        col_w = (w - gap) // 2
        left_y = self._draw_card(screen, x, cy, col_w, 260, "SPECIES POPULATION HISTORY",
                                lambda sx, sy, sw, sh: self._draw_species_history(screen, sx, sy, sw, sh))
        right_y = self._draw_card(screen, x + col_w + gap, cy, col_w, 260, "GENDER BALANCE",
                                 lambda sx, sy, sw, sh: self._draw_gender_chart(screen, sx, sy, sw, sh))
        cy = max(left_y, right_y)
        cy += gap

        # Row 4: Trait evolution + Species distribution bars (taller for current values)
        left_y = self._draw_card(screen, x, cy, col_w, 240, "TRAIT EVOLUTION",
                                lambda sx, sy, sw, sh: self._draw_trait_evolution(screen, sx, sy, sw, sh))
        right_y = self._draw_card(screen, x + col_w + gap, cy, col_w, 240, "SPECIES DISTRIBUTION",
                                 lambda sx, sy, sw, sh: self._draw_species_bars(screen, sx, sy, sw, sh, live_agents))
        cy = max(left_y, right_y)
        cy += gap

        # Row 5: Behavioral pie + Vitals histograms (taller for detailed stats)
        left_y = self._draw_card(screen, x, cy, col_w, 270, "BEHAVIORAL ANALYSIS",
                                lambda sx, sy, sw, sh: self._draw_behavior_chart(screen, sx, sy, sw, sh, live_agents))
        right_y = self._draw_card(screen, x + col_w + gap, cy, col_w, 270, "VITALS DISTRIBUTION",
                                 lambda sx, sy, sw, sh: self._draw_vitals_histograms(screen, sx, sy, sw, sh, live_agents))
        cy = max(left_y, right_y)
        cy += gap

        # Row 6: Generation stats + Combat stats (taller for comprehensive data)
        left_y = self._draw_card(screen, x, cy, col_w, 220, "GENERATION ANALYSIS",
                                lambda sx, sy, sw, sh: self._draw_generation_stats(screen, sx, sy, sw, sh, live_agents))
        right_y = self._draw_card(screen, x + col_w + gap, cy, col_w, 220, "COMBAT & REPRODUCTION",
                                 lambda sx, sy, sw, sh: self._draw_combat_stats(screen, sx, sy, sw, sh, live_agents))
        cy = max(left_y, right_y)
        cy += gap

        # Row 7: Per-species gender breakdown (full width)
        cy = self._draw_card(screen, x, cy, w, 280, "GENDER BY SPECIES",
                            lambda sx, sy, sw, sh: self._draw_species_gender(screen, sx, sy, sw, sh, live_agents))

        return cy - y

    def _draw_card(self, screen, x, y, w, h, title, draw_func):
        """Draw a card with header and content."""
        # Card background
        pygame.draw.rect(screen, self.card_color, (x, y, w, h), border_radius=6)
        pygame.draw.rect(screen, self.border_color, (x, y, w, h), 1, border_radius=6)

        # Header
        header_h = 28
        pygame.draw.rect(screen, self.card_header_color, (x, y, w, header_h), border_top_left_radius=6, border_top_right_radius=6)

        title_surf = self.font_header.render(title, True, self.accent_color)
        screen.blit(title_surf, (x + 12, y + 6))

        # Content area
        content_x = x + 10
        content_y = y + header_h + 8
        content_w = w - 20
        content_h = h - header_h - 16

        draw_func(content_x, content_y, content_w, content_h)

        return y + h

    def _draw_metrics_row(self, screen, x, y, w, live_agents):
        """Draw key metrics cards row with enhanced statistics."""
        metrics = []
        total = len(live_agents)
        latest = self.stats_collector.latest if self.stats_collector else None
        snaps = self.stats_collector.snapshots if self.stats_collector else []

        # Calculate trend (compare with earlier snapshot)
        def get_trend(current, history_attr):
            if len(snaps) >= 10:
                old_val = getattr(snaps[-10], history_attr, current)
                if current > old_val:
                    return "↑"
                elif current < old_val:
                    return "↓"
            return "→"

        # Calculate metrics
        if total > 0:
            males = sum(1 for a in live_agents if getattr(a, 'sex', '') == 'male')
            females = total - males
            species = len(set(a.species_id for a in live_agents))
            avg_energy = sum(a.energy for a in live_agents) / total
            avg_hydration = sum(a.hydration for a in live_agents) / total
            avg_age = sum(a.age for a in live_agents) / total
            max_gen = max(a.generation for a in live_agents)
            avg_gen = sum(a.generation for a in live_agents) / total

            # Calculate rates from snapshots
            births_rate = 0.0
            deaths_rate = 0.0
            if len(snaps) >= 5:
                time_span = snaps[-1].time - snaps[-5].time
                if time_span > 0:
                    births_rate = (snaps[-1].total_births - snaps[-5].total_births) / time_span
                    deaths_rate = (snaps[-1].total_deaths - snaps[-5].total_deaths) / time_span

            pop_trend = get_trend(total, 'agent_count')
            energy_trend = get_trend(avg_energy, 'avg_energy')

            metrics = [
                ("POPULATION", f"{total}", f"M:{males} F:{females} {pop_trend}", self.accent_color,
                 f"+{births_rate:.1f}/s -{deaths_rate:.1f}/s"),
                ("SPECIES", str(species), f"Div: {latest.genetic_diversity:.3f}" if latest else "-", (180, 140, 255),
                 f"Extinct: {len(self.stats_collector.known_species) - species}" if self.stats_collector else "-"),
                ("AVG ENERGY", f"{avg_energy:.0f}", f"Min:{min(a.energy for a in live_agents):.0f} Max:{max(a.energy for a in live_agents):.0f}", self.energy_color,
                 f"Trend: {energy_trend}"),
                ("AVG HYDRA", f"{avg_hydration:.0f}", f"Min:{min(a.hydration for a in live_agents):.0f} Max:{max(a.hydration for a in live_agents):.0f}", self.hydration_color,
                 f"Thirsty: {sum(1 for a in live_agents if a.hydration < 50)}"),
                ("AVG AGE", f"{avg_age:.1f}s", f"Oldest: {max(a.age for a in live_agents):.1f}s", (255, 200, 100),
                 f"Young(<5s): {sum(1 for a in live_agents if a.age < 5)}"),
                ("GENERATION", str(max_gen), f"Avg: {avg_gen:.1f} Min: {min(a.generation for a in live_agents)}", (100, 200, 200),
                 f"Founders: {sum(1 for a in live_agents if a.generation == 0)}"),
            ]
        else:
            metrics = [
                ("POPULATION", "0", "EXTINCT", (255, 80, 80), "Simulation ended"),
                ("SPECIES", "0", "-", self.text_dim, "-"),
                ("AVG ENERGY", "-", "-", self.text_dim, "-"),
                ("AVG HYDRA", "-", "-", self.text_dim, "-"),
                ("AVG AGE", "-", "-", self.text_dim, "-"),
                ("GENERATION", "-", "-", self.text_dim, "-"),
            ]

        card_w = (w - 10 * (len(metrics) - 1)) // len(metrics)
        card_h = 85

        for i, (label, value, sub, color, extra) in enumerate(metrics):
            cx = x + i * (card_w + 10)

            pygame.draw.rect(screen, self.card_color, (cx, y, card_w, card_h), border_radius=6)
            pygame.draw.rect(screen, color, (cx, y, card_w, 3), border_top_left_radius=6, border_top_right_radius=6)
            pygame.draw.rect(screen, self.border_color, (cx, y, card_w, card_h), 1, border_radius=6)

            label_surf = self.font_tiny.render(label, True, self.text_dim)
            screen.blit(label_surf, (cx + 10, y + 8))

            value_surf = self.font_large.render(value, True, color)
            screen.blit(value_surf, (cx + 10, y + 22))

            sub_surf = self.font_tiny.render(sub, True, self.text_dim)
            screen.blit(sub_surf, (cx + 10, y + 48))

            extra_surf = self.font_tiny.render(extra, True, self.text_dim)
            screen.blit(extra_surf, (cx + 10, y + 62))

        return y + card_h

    def _draw_population_timeline(self, screen, x, y, w, h):
        """Draw population over time with filled area, stats, and markers."""
        if not self.stats_collector.snapshots or len(self.stats_collector.snapshots) < 2:
            self._draw_no_data(screen, x, y, w, h)
            return

        snaps = self.stats_collector.snapshots
        max_time = max(s.time for s in snaps)
        populations = [s.agent_count for s in snaps]
        max_pop = max(max(populations), 10)
        min_pop = min(populations)
        avg_pop = sum(populations) / len(populations)

        # Find peak and trough indices
        peak_idx = populations.index(max(populations))
        trough_idx = populations.index(min(populations))

        # Graph area (leave space for stats on right)
        gx, gy, gw, gh = x + 45, y + 5, w - 180, h - 45

        # Grid
        self._draw_grid(screen, gx, gy, gw, gh, 5, 5, max_pop, max_time, "Pop", "Time(s)")

        # Draw filled area
        points = []
        for snap in snaps:
            px = gx + (snap.time / max_time) * gw
            py = gy + gh - (snap.agent_count / max_pop) * gh
            points.append((px, py))

        if len(points) > 1:
            # Fill
            fill_pts = [(gx, gy + gh)] + points + [(gx + gw, gy + gh)]
            pygame.draw.polygon(screen, (*self.accent_color[:3], 40), fill_pts)
            # Line
            pygame.draw.lines(screen, self.accent_color, False, points, 2)
            # End marker
            pygame.draw.circle(screen, self.accent_color, (int(points[-1][0]), int(points[-1][1])), 4)

            # Mark peak
            if peak_idx < len(points):
                px, py = points[peak_idx]
                pygame.draw.circle(screen, (100, 255, 100), (int(px), int(py)), 5)
                peak_label = self.font_tiny.render(f"Peak: {max(populations)}", True, (100, 255, 100))
                screen.blit(peak_label, (int(px) - 20, int(py) - 15))

            # Mark trough (if different from current)
            if trough_idx < len(points) and trough_idx != len(points) - 1:
                px, py = points[trough_idx]
                pygame.draw.circle(screen, (255, 100, 100), (int(px), int(py)), 5)

        # Moving average line (10 sample window)
        if len(snaps) > 10:
            ma_points = []
            window = 10
            for i in range(window - 1, len(snaps)):
                avg = sum(snaps[j].agent_count for j in range(i - window + 1, i + 1)) / window
                px = gx + (snaps[i].time / max_time) * gw
                py = gy + gh - (avg / max_pop) * gh
                ma_points.append((px, py))
            if len(ma_points) > 1:
                pygame.draw.lines(screen, (255, 200, 100), False, ma_points, 1)

        # Stats panel on right
        sx = x + w - 125
        sy = y + 5
        stats = [
            ("Current:", f"{populations[-1]}", self.accent_color),
            ("Peak:", f"{max(populations)}", (100, 255, 100)),
            ("Low:", f"{min(populations)}", (255, 100, 100)),
            ("Average:", f"{avg_pop:.1f}", (255, 200, 100)),
            ("Std Dev:", f"{(sum((p - avg_pop)**2 for p in populations) / len(populations))**0.5:.1f}", self.text_dim),
        ]

        for label, value, color in stats:
            label_surf = self.font_tiny.render(label, True, self.text_dim)
            value_surf = self.font_small.render(value, True, color)
            screen.blit(label_surf, (sx, sy))
            screen.blit(value_surf, (sx + 55, sy))
            sy += 16

        # Growth rate
        sy += 8
        if len(snaps) >= 2 and snaps[-1].time > snaps[0].time:
            growth = (populations[-1] - populations[0]) / (snaps[-1].time - snaps[0].time)
            growth_color = (100, 200, 100) if growth > 0 else (255, 100, 100) if growth < 0 else self.text_dim
            growth_text = self.font_tiny.render(f"Growth: {growth:+.2f}/s", True, growth_color)
            screen.blit(growth_text, (sx, sy))

        # Legend
        ly = y + h - 22
        pygame.draw.line(screen, self.accent_color, (gx, ly + 5), (gx + 20, ly + 5), 2)
        screen.blit(self.font_tiny.render("Population", True, self.text_color), (gx + 25, ly))
        pygame.draw.line(screen, (255, 200, 100), (gx + 100, ly + 5), (gx + 120, ly + 5), 1)
        screen.blit(self.font_tiny.render("Moving Avg", True, self.text_color), (gx + 125, ly))

    def _draw_species_history(self, screen, x, y, w, h):
        """Draw species population history with extinction tracking."""
        if not self.stats_collector.snapshots or len(self.stats_collector.snapshots) < 2:
            self._draw_no_data(screen, x, y, w, h)
            return

        snaps = self.stats_collector.snapshots
        known = self.stats_collector.known_species
        if not known:
            return

        max_time = max(s.time for s in snaps)
        max_pop = 1
        for snap in snaps:
            for count in snap.species_counts.values():
                max_pop = max(max_pop, count)
        max_pop = max(10, max_pop)

        # Graph area
        gx, gy, gw, gh = x + 40, y + 5, w - 140, h - 35

        # Grid
        self._draw_grid(screen, gx, gy, gw, gh, 4, 4, max_pop, max_time)

        # Sort species by current population
        current = {sid: snaps[-1].species_counts.get(sid, 0) for sid in known}
        sorted_species = sorted(known, key=lambda s: current.get(s, 0), reverse=True)

        # Separate active and extinct
        active_species = [s for s in sorted_species if current.get(s, 0) > 0]
        extinct_species = [s for s in sorted_species if current.get(s, 0) == 0]

        # Draw lines for active species
        for i, sid in enumerate(active_species[:8]):
            color = self.get_species_color(sid)
            points = []
            for snap in snaps:
                count = snap.species_counts.get(sid, 0)
                px = gx + (snap.time / max_time) * gw
                py = gy + gh - (count / max_pop) * gh
                points.append((px, py))
            if len(points) > 1:
                pygame.draw.lines(screen, color, False, points, 2)
                # End marker
                pygame.draw.circle(screen, color, (int(points[-1][0]), int(points[-1][1])), 3)

        # Draw faded lines for recently extinct (first 2)
        for i, sid in enumerate(extinct_species[:2]):
            color = self.get_species_color(sid)
            faded_color = (color[0] // 3, color[1] // 3, color[2] // 3)
            points = []
            for snap in snaps:
                count = snap.species_counts.get(sid, 0)
                px = gx + (snap.time / max_time) * gw
                py = gy + gh - (count / max_pop) * gh
                points.append((px, py))
            if len(points) > 1:
                pygame.draw.lines(screen, faded_color, False, points, 1)

        # Legend panel
        lx = x + w - 95
        ly = y + 3

        # Active species
        header = self.font_tiny.render("Active:", True, self.accent_color)
        screen.blit(header, (lx, ly))
        ly += 12

        for i, sid in enumerate(active_species[:6]):
            color = self.get_species_color(sid)
            name = self.get_species_name(sid)[:6]
            count = current.get(sid, 0)

            self._draw_shape_indicator(screen, lx + 5, ly + 5, 7, sid)
            text = self.font_tiny.render(f"{name}:{count}", True, color)
            screen.blit(text, (lx + 13, ly))
            ly += 12

        # Extinct count
        if extinct_species:
            ly += 4
            extinct_text = self.font_tiny.render(f"Extinct: {len(extinct_species)}", True, (150, 100, 100))
            screen.blit(extinct_text, (lx, ly))

        # Stats at bottom
        total_active = len(active_species)
        total_known = len(known)
        stats_text = self.font_tiny.render(f"Species: {total_active}/{total_known}", True, self.text_dim)
        screen.blit(stats_text, (gx, gy + gh + 5))

    def _draw_gender_chart(self, screen, x, y, w, h):
        """Draw gender distribution over time with detailed stats."""
        if not self.stats_collector.snapshots or len(self.stats_collector.snapshots) < 2:
            self._draw_no_data(screen, x, y, w, h)
            return

        snaps = self.stats_collector.snapshots

        # Graph area (left side)
        gx, gy, gw, gh = x + 35, y + 5, w - 155, h - 35

        max_time = max(s.time for s in snaps)
        max_count = max(max(s.total_males, s.total_females, 1) for s in snaps)

        # Grid
        self._draw_grid(screen, gx, gy, gw, gh, 4, 4, max_count, max_time)

        # Lines
        male_pts = []
        female_pts = []
        ratios = []
        for snap in snaps:
            px = gx + (snap.time / max_time) * gw
            male_pts.append((px, gy + gh - (snap.total_males / max_count) * gh))
            female_pts.append((px, gy + gh - (snap.total_females / max_count) * gh))
            if snap.total_females > 0:
                ratios.append(snap.total_males / snap.total_females)

        if len(male_pts) > 1:
            pygame.draw.lines(screen, self.male_color, False, male_pts, 2)
            pygame.draw.lines(screen, self.female_color, False, female_pts, 2)
            # End markers
            pygame.draw.circle(screen, self.male_color, (int(male_pts[-1][0]), int(male_pts[-1][1])), 3)
            pygame.draw.circle(screen, self.female_color, (int(female_pts[-1][0]), int(female_pts[-1][1])), 3)

        # Legend
        ly = gy + gh + 5
        pygame.draw.line(screen, self.male_color, (gx, ly + 4), (gx + 15, ly + 4), 2)
        screen.blit(self.font_tiny.render("Male", True, self.text_color), (gx + 18, ly))
        pygame.draw.line(screen, self.female_color, (gx + 60, ly + 4), (gx + 75, ly + 4), 2)
        screen.blit(self.font_tiny.render("Female", True, self.text_color), (gx + 78, ly))

        # Right panel with pie chart and stats
        latest = snaps[-1]
        total = latest.total_males + latest.total_females

        if total > 0:
            # Pie chart
            cx, cy_pie = x + w - 55, y + 55
            radius = 35

            male_pct = latest.total_males / total
            male_angle = male_pct * 2 * math.pi
            self._draw_pie_slice(screen, cx, cy_pie, radius, 0, male_angle, self.male_color)
            self._draw_pie_slice(screen, cx, cy_pie, radius, male_angle, 2 * math.pi, self.female_color)

            # Center hole with ratio
            pygame.draw.circle(screen, self.card_color, (cx, cy_pie), radius // 2)
            ratio = latest.total_males / latest.total_females if latest.total_females > 0 else 0
            ratio_text = self.font_tiny.render(f"{ratio:.1f}", True, self.text_color)
            screen.blit(ratio_text, (cx - ratio_text.get_width()//2, cy_pie - 5))

            # Stats below pie
            sy = y + 100
            stats = [
                (f"M: {latest.total_males} ({male_pct*100:.0f}%)", self.male_color),
                (f"F: {latest.total_females} ({(1-male_pct)*100:.0f}%)", self.female_color),
            ]

            for stat_text, color in stats:
                surf = self.font_tiny.render(stat_text, True, color)
                screen.blit(surf, (x + w - 95, sy))
                sy += 13

            # Ratio trend
            if len(ratios) >= 2:
                ratio_trend = "↑" if ratios[-1] > ratios[0] else "↓" if ratios[-1] < ratios[0] else "→"
                trend_color = self.male_color if ratios[-1] > ratios[0] else self.female_color
                trend_text = self.font_tiny.render(f"Ratio: {ratio:.2f} {ratio_trend}", True, trend_color)
                screen.blit(trend_text, (x + w - 95, sy))

            # Balance indicator
            sy += 15
            balance = abs(0.5 - male_pct)
            if balance < 0.05:
                balance_text = "Balanced"
                balance_color = (100, 200, 100)
            elif balance < 0.15:
                balance_text = "Slight imbalance"
                balance_color = (255, 200, 100)
            else:
                balance_text = "Imbalanced!"
                balance_color = (255, 100, 100)
            bal_surf = self.font_tiny.render(balance_text, True, balance_color)
            screen.blit(bal_surf, (x + w - 95, sy))

    def _draw_trait_evolution(self, screen, x, y, w, h):
        """Draw trait evolution with legend and current values."""
        if not self.stats_collector.snapshots or len(self.stats_collector.snapshots) < 2:
            self._draw_no_data(screen, x, y, w, h)
            return

        snaps = self.stats_collector.snapshots
        max_time = max(s.time for s in snaps)
        latest = snaps[-1]

        traits = [
            ("Speed", "avg_speed", 6.0, (100, 220, 150)),
            ("Size", "avg_size", 12.0, (100, 160, 255)),
            ("Aggression", "avg_aggression", 2.0, (255, 100, 120)),
            ("Vision", "avg_vision", 200.0, (255, 200, 100)),
        ]

        # Graph area (smaller to fit stats)
        gx, gy, gw, gh = x + 40, y + 5, w - 150, h - 50

        # Grid
        self._draw_grid(screen, gx, gy, gw, gh, 4, 4, 1.0, max_time, "Norm", "")

        # Draw lines and collect data
        trait_data = {}
        for name, attr, max_val, color in traits:
            points = []
            values = []
            for snap in snaps:
                val = getattr(snap, attr, 0)
                values.append(val)
                norm_val = val / max_val
                px = gx + (snap.time / max_time) * gw
                py = gy + gh - min(1.0, norm_val) * gh
                points.append((px, py))
            if len(points) > 1:
                pygame.draw.lines(screen, color, False, points, 2)
            trait_data[name] = {
                'current': values[-1] if values else 0,
                'max_val': max_val,
                'change': values[-1] - values[0] if len(values) > 1 else 0
            }

        # Current values panel on right
        sx = x + w - 105
        sy = y + 5
        header = self.font_tiny.render("Current Values:", True, self.accent_color)
        screen.blit(header, (sx, sy))
        sy += 14

        for name, attr, max_val, color in traits:
            data = trait_data.get(name, {})
            current = data.get('current', 0)
            change = data.get('change', 0)

            # Trend indicator
            trend = "↑" if change > 0.1 else "↓" if change < -0.1 else "→"
            trend_color = (100, 200, 100) if change > 0.1 else (255, 100, 100) if change < -0.1 else self.text_dim

            val_text = self.font_tiny.render(f"{name[:5]}:", True, color)
            screen.blit(val_text, (sx, sy))
            val_num = self.font_tiny.render(f"{current:.2f}", True, self.text_color)
            screen.blit(val_num, (sx + 40, sy))
            trend_surf = self.font_tiny.render(trend, True, trend_color)
            screen.blit(trend_surf, (sx + 80, sy))
            sy += 13

        # Min/Max info
        sy += 5
        divider = self.font_tiny.render("───────────", True, self.border_color)
        screen.blit(divider, (sx, sy))
        sy += 12

        for name, attr, max_val, color in traits[:3]:  # Only first 3 for space
            all_vals = [getattr(s, attr, 0) for s in snaps]
            if all_vals:
                min_v = min(all_vals)
                max_v = max(all_vals)
                range_text = self.font_tiny.render(f"{name[:3]}: {min_v:.1f}-{max_v:.1f}", True, self.text_dim)
                screen.blit(range_text, (sx, sy))
                sy += 12

        # Legend at bottom
        lx = x + 10
        ly = y + h - 20
        for name, _, _, color in traits:
            pygame.draw.line(screen, color, (lx, ly + 5), (lx + 15, ly + 5), 2)
            label = self.font_tiny.render(name[:4], True, self.text_color)
            screen.blit(label, (lx + 18, ly))
            lx += 65

    def _draw_species_bars(self, screen, x, y, w, h, live_agents):
        """Draw species distribution as horizontal bars with shapes and trend indicators."""
        species_counts = defaultdict(int)
        species_ages = defaultdict(list)
        species_energy = defaultdict(list)
        for a in live_agents:
            species_counts[a.species_id] += 1
            species_ages[a.species_id].append(a.age)
            species_energy[a.species_id].append(a.energy)

        if not species_counts:
            self._draw_no_data(screen, x, y, w, h)
            return

        # Get historical data for trends
        snaps = self.stats_collector.snapshots if self.stats_collector else []
        old_counts = {}
        if len(snaps) >= 10:
            old_counts = snaps[-10].species_counts

        sorted_species = sorted(species_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        total = sum(c for _, c in sorted_species)
        max_count = sorted_species[0][1] if sorted_species else 1

        bar_h = 18
        by = y
        for sid, count in sorted_species:
            color = self.get_species_color(sid)
            name = self.get_species_name(sid)
            pct = (count / total) * 100

            # Calculate trend
            old_count = old_counts.get(sid, count)
            trend = "↑" if count > old_count else "↓" if count < old_count else "→"
            trend_color = (100, 200, 100) if count > old_count else (255, 100, 100) if count < old_count else self.text_dim

            # Shape indicator
            self._draw_shape_indicator(screen, x + 8, by + bar_h // 2, 10, sid)

            # Bar background
            bar_w = w - 135
            pygame.draw.rect(screen, (50, 55, 65), (x + 20, by + 2, bar_w, bar_h - 4), border_radius=2)

            # Bar fill
            fill_w = int((count / max_count) * bar_w)
            if fill_w > 0:
                pygame.draw.rect(screen, color, (x + 20, by + 2, fill_w, bar_h - 4), border_radius=2)

            # Name (on bar)
            name_surf = self.font_tiny.render(name[:7], True, (255, 255, 255))
            screen.blit(name_surf, (x + 25, by + 3))

            # Avg age indicator (small bar inside)
            if species_ages[sid]:
                avg_age = sum(species_ages[sid]) / len(species_ages[sid])
                age_indicator = self.font_tiny.render(f"~{avg_age:.0f}s", True, (200, 200, 200))
                screen.blit(age_indicator, (x + 20 + fill_w - 25, by + 3))

            # Count and percentage
            count_surf = self.font_tiny.render(f"{count} ({pct:.0f}%)", True, self.text_dim)
            screen.blit(count_surf, (x + w - 100, by + 3))

            # Trend indicator
            trend_surf = self.font_small.render(trend, True, trend_color)
            screen.blit(trend_surf, (x + w - 25, by + 2))

            by += bar_h + 1

        # Summary stats at bottom
        if by < y + h - 20:
            by = y + h - 18
            total_species = len(species_counts)
            extinct = len(self.stats_collector.known_species) - total_species if self.stats_collector else 0
            summary = self.font_tiny.render(f"Active: {total_species} | Extinct: {extinct} | Total pop: {total}", True, self.text_dim)
            screen.blit(summary, (x, by))

    def _draw_behavior_chart(self, screen, x, y, w, h, live_agents):
        """Draw behavioral analysis with pie chart, stats, and detailed breakdowns."""
        total = len(live_agents)
        if total == 0:
            self._draw_no_data(screen, x, y, w, h)
            return

        attacking = sum(1 for a in live_agents if getattr(a, 'attack_intent', 0) > 0.5)
        fleeing = sum(1 for a in live_agents if getattr(a, 'attack_intent', 0) < -0.5)
        mating = sum(1 for a in live_agents if getattr(a, 'mate_desire', 0) > 0.5)
        neutral = total - attacking - fleeing - mating

        # Additional behavioral metrics
        hungry = sum(1 for a in live_agents if a.energy < 50)
        thirsty = sum(1 for a in live_agents if a.hydration < 50)
        low_health = sum(1 for a in live_agents if a.energy < 30 or a.hydration < 30)

        behaviors = [
            ("Attacking", attacking, (255, 90, 90)),
            ("Fleeing", fleeing, (255, 200, 80)),
            ("Mating", mating, (255, 130, 180)),
            ("Neutral", neutral, (100, 200, 130)),
        ]

        # Pie chart
        cx, cy_pie = x + 70, y + h // 2 - 15
        radius = 55

        start = 0
        for name, count, color in behaviors:
            if count > 0:
                angle = (count / total) * 2 * math.pi
                self._draw_pie_slice(screen, cx, cy_pie, radius, start, start + angle, color)
                start += angle

        pygame.draw.circle(screen, self.card_color, (cx, cy_pie), radius // 2)

        # Center label
        center_text = self.font_tiny.render(f"{total}", True, self.text_color)
        screen.blit(center_text, (cx - center_text.get_width()//2, cy_pie - 5))

        # Legend with percentages
        lx = x + 145
        ly = y + 8
        for name, count, color in behaviors:
            pct = (count / total) * 100
            pygame.draw.rect(screen, color, (lx, ly + 2, 10, 10))
            text = self.font_tiny.render(f"{name}: {count} ({pct:.0f}%)", True, self.text_color)
            screen.blit(text, (lx + 14, ly))
            ly += 16

        # Detailed stats section
        ly += 8
        pygame.draw.line(screen, self.border_color, (lx, ly), (lx + 140, ly), 1)
        ly += 6

        # Intent averages
        avg_attack = sum(getattr(a, 'attack_intent', 0) for a in live_agents) / total
        avg_mate = sum(getattr(a, 'mate_desire', 0) for a in live_agents) / total
        avg_aggression = sum(getattr(a, 'aggression', 1) for a in live_agents) / total

        stats = [
            (f"Avg Attack: {avg_attack:+.2f}", (255, 150, 150) if avg_attack > 0 else self.text_dim),
            (f"Avg Mate: {avg_mate:+.2f}", (255, 180, 200) if avg_mate > 0.3 else self.text_dim),
            (f"Avg Aggro: {avg_aggression:.2f}", (255, 120, 120) if avg_aggression > 1.2 else self.text_dim),
        ]

        for stat_text, color in stats:
            surf = self.font_tiny.render(stat_text, True, color)
            screen.blit(surf, (lx, ly))
            ly += 13

        # Needs section
        ly += 5
        pygame.draw.line(screen, self.border_color, (lx, ly), (lx + 140, ly), 1)
        ly += 6
        needs_header = self.font_tiny.render("Agent Needs:", True, self.accent_color)
        screen.blit(needs_header, (lx, ly))
        ly += 13

        needs = [
            (f"Hungry (<50E): {hungry} ({hungry*100//total}%)", self.energy_color),
            (f"Thirsty (<50H): {thirsty} ({thirsty*100//total}%)", self.hydration_color),
            (f"Critical: {low_health} ({low_health*100//total}%)", (255, 80, 80)),
        ]

        for need_text, color in needs:
            surf = self.font_tiny.render(need_text, True, color)
            screen.blit(surf, (lx, ly))
            ly += 12

    def _draw_vitals_histograms(self, screen, x, y, w, h, live_agents):
        """Draw energy and hydration histograms with detailed stats."""
        if not live_agents:
            self._draw_no_data(screen, x, y, w, h)
            return

        # Energy histogram
        hy = y
        self._draw_histogram(screen, x, hy, w, (h - 20) // 2, live_agents,
                            'energy', 300, self.energy_color, "ENERGY DISTRIBUTION")

        # Hydration histogram
        hy = y + (h - 20) // 2 + 20
        self._draw_histogram(screen, x, hy, w, (h - 20) // 2, live_agents,
                            'hydration', 150, self.hydration_color, "HYDRATION DISTRIBUTION")

    def _draw_histogram(self, screen, x, y, w, h, agents, attr, max_val, color, label):
        """Draw a histogram for an attribute with percentiles and detailed stats."""
        label_surf = self.font_tiny.render(label, True, color)
        screen.blit(label_surf, (x, y))

        values = sorted([getattr(a, attr, 0) for a in agents])
        n = len(values)
        avg_val = sum(values) / n
        min_val = values[0]
        max_v = values[-1]

        # Calculate percentiles
        p25 = values[n // 4] if n >= 4 else min_val
        p50 = values[n // 2] if n >= 2 else avg_val
        p75 = values[3 * n // 4] if n >= 4 else max_v

        # Calculate std dev
        std_dev = (sum((v - avg_val) ** 2 for v in values) / n) ** 0.5

        # Bins
        bins = [0] * 10
        for v in values:
            idx = min(9, int(v / (max_val / 10)))
            bins[idx] += 1

        max_bin = max(bins) if max(bins) > 0 else 1
        bin_w = (w - 140) // 10
        bx = x
        by = y + 15
        bh = h - 35

        # Draw bins with gradient based on value range
        for i, count in enumerate(bins):
            bar_h = int((count / max_bin) * bh)
            # Color intensity based on whether this is a "good" or "bad" range
            if i < 3:  # Low values - warning
                bar_color = (color[0], int(color[1] * 0.6), int(color[2] * 0.6))
            elif i > 7:  # High values - good
                bar_color = (int(color[0] * 0.8), color[1], int(color[2] * 0.8))
            else:
                bar_color = color

            if bar_h > 0:
                pygame.draw.rect(screen, bar_color, (bx + i * bin_w, by + bh - bar_h, bin_w - 2, bar_h))

            # Bin label at bottom
            if i % 3 == 0:
                bin_label = self.font_tiny.render(f"{int(i * max_val / 10)}", True, self.text_dim)
                screen.blit(bin_label, (bx + i * bin_w, by + bh + 2))

        # Draw median line
        median_x = bx + (p50 / max_val) * (10 * bin_w)
        pygame.draw.line(screen, (255, 255, 100), (median_x, by), (median_x, by + bh), 2)

        # Stats panel on right
        sx = x + w - 130
        sy = y + 2

        stats = [
            (f"Avg: {avg_val:.0f}", self.text_color),
            (f"Med: {p50:.0f}", (255, 255, 100)),
            (f"Min: {min_val:.0f}", (255, 150, 150) if min_val < max_val * 0.2 else self.text_dim),
            (f"Max: {max_v:.0f}", self.text_dim),
            (f"σ: {std_dev:.1f}", self.text_dim),
        ]

        for stat_text, stat_color in stats:
            surf = self.font_tiny.render(stat_text, True, stat_color)
            screen.blit(surf, (sx, sy))
            sy += 11

        # Percentile bar
        sy += 2
        pbar_w = 50
        pygame.draw.rect(screen, (50, 55, 65), (sx, sy, pbar_w, 8), border_radius=2)
        p25_x = int((p25 / max_val) * pbar_w)
        p75_x = int((p75 / max_val) * pbar_w)
        pygame.draw.rect(screen, color, (sx + p25_x, sy, p75_x - p25_x, 8), border_radius=2)
        pbar_label = self.font_tiny.render("25-75%", True, self.text_dim)
        screen.blit(pbar_label, (sx + pbar_w + 5, sy - 1))

    def _draw_generation_stats(self, screen, x, y, w, h, live_agents):
        """Draw comprehensive generation statistics."""
        if not live_agents:
            self._draw_no_data(screen, x, y, w, h)
            return

        gens = [a.generation for a in live_agents]
        avg_gen = sum(gens) / len(gens)
        max_gen = max(gens)
        min_gen = min(gens)
        total_mut = sum(getattr(a, 'total_mutations', 0) for a in live_agents)
        somatic_mut = sum(getattr(a, 'somatic_mutations', 0) for a in live_agents)

        # Generation spread (diversity measure)
        gen_spread = max_gen - min_gen

        # Count founders (gen 0) vs evolved
        founders = sum(1 for g in gens if g == 0)
        evolved = len(gens) - founders

        # Left column - stats
        col1_x = x
        sy = y

        stats_left = [
            ("Avg Gen:", f"{avg_gen:.1f}", self.text_color),
            ("Max Gen:", f"{max_gen}", (100, 200, 100)),
            ("Min Gen:", f"{min_gen}", self.text_dim),
            ("Spread:", f"{gen_spread}", self.accent_color),
        ]

        for label, value, color in stats_left:
            label_surf = self.font_tiny.render(label, True, self.text_dim)
            value_surf = self.font_small.render(value, True, color)
            screen.blit(label_surf, (col1_x, sy))
            screen.blit(value_surf, (col1_x + 55, sy))
            sy += 15

        # Right column - mutation stats
        col2_x = x + w // 2
        sy = y

        stats_right = [
            ("Mutations:", f"{total_mut}", (255, 180, 100)),
            ("Somatic:", f"{somatic_mut}", (255, 150, 80)),
            ("Mut/Agent:", f"{total_mut / len(live_agents):.1f}", self.text_dim),
            ("Founders:", f"{founders} ({founders*100//len(gens)}%)", self.text_dim),
        ]

        for label, value, color in stats_right:
            label_surf = self.font_tiny.render(label, True, self.text_dim)
            value_surf = self.font_small.render(value, True, color)
            screen.blit(label_surf, (col2_x, sy))
            screen.blit(value_surf, (col2_x + 60, sy))
            sy += 15

        # Generation distribution bars
        gen_counts = defaultdict(int)
        for g in gens:
            gen_counts[g] += 1

        sy = y + 68
        label = self.font_tiny.render("Generation Distribution:", True, self.accent_color)
        screen.blit(label, (x, sy))
        sy += 14

        sorted_gens = sorted(gen_counts.items())
        display_gens = sorted_gens[:10] if len(sorted_gens) <= 10 else sorted_gens[:5] + sorted_gens[-5:]

        if display_gens:
            max_count = max(c for _, c in display_gens)
            bar_w = (w - 10) // len(display_gens)
            bar_max_h = 40

            for i, (gen, count) in enumerate(display_gens):
                bar_h = int((count / max_count) * bar_max_h)
                bx = x + i * bar_w

                # Color gradient based on generation
                intensity = min(1.0, gen / max(max_gen, 1))
                bar_color = (int(100 + 100 * intensity), int(150 - 50 * intensity), 220)

                pygame.draw.rect(screen, bar_color, (bx, sy + bar_max_h - bar_h, bar_w - 3, bar_h))

                # Generation label
                gen_text = self.font_tiny.render(f"G{gen}", True, self.text_dim)
                screen.blit(gen_text, (bx, sy + bar_max_h + 2))

                # Count on top of bar
                if bar_h > 12:
                    count_text = self.font_tiny.render(f"{count}", True, (255, 255, 255))
                    screen.blit(count_text, (bx + 2, sy + bar_max_h - bar_h + 2))

    def _draw_combat_stats(self, screen, x, y, w, h, live_agents):
        """Draw comprehensive combat and reproduction statistics."""
        if not live_agents:
            self._draw_no_data(screen, x, y, w, h)
            return

        total = len(live_agents)
        total_kills = sum(getattr(a, 'kills', 0) for a in live_agents)
        total_offspring = sum(getattr(a, 'offspring_count', 0) for a in live_agents)
        attackers = sum(1 for a in live_agents if getattr(a, 'attack_intent', 0) > 0.5)
        maters = sum(1 for a in live_agents if getattr(a, 'mate_desire', 0) > 0.5)

        # Find record holders
        oldest = max(live_agents, key=lambda a: a.age)
        most_kills = max(live_agents, key=lambda a: getattr(a, 'kills', 0))
        most_offspring = max(live_agents, key=lambda a: getattr(a, 'offspring_count', 0))

        # Calculate rates from snapshots
        snaps = self.stats_collector.snapshots if self.stats_collector else []
        kill_rate = 0.0
        birth_rate = 0.0
        death_rate = 0.0
        if len(snaps) >= 5:
            time_span = snaps[-1].time - snaps[-5].time
            if time_span > 0:
                kill_rate = (snaps[-1].total_kills - snaps[-5].total_kills) / time_span
                birth_rate = (snaps[-1].total_births - snaps[-5].total_births) / time_span
                death_rate = (snaps[-1].total_deaths - snaps[-5].total_deaths) / time_span

        # Calculate killers percentage
        killers = sum(1 for a in live_agents if getattr(a, 'kills', 0) > 0)
        parents = sum(1 for a in live_agents if getattr(a, 'offspring_count', 0) > 0)

        col1_x = x
        col2_x = x + w // 2 + 5

        # Combat section
        combat_header = self.font_tiny.render("COMBAT", True, (255, 100, 100))
        screen.blit(combat_header, (col1_x, y))

        stats_left = [
            ("Kills:", f"{total_kills}", (255, 100, 100)),
            ("Kill Rate:", f"{kill_rate:.2f}/s", (255, 130, 130)),
            ("Attackers:", f"{attackers} ({attackers*100//total}%)", (255, 150, 100)),
            ("Killers:", f"{killers} ({killers*100//total}%)", (220, 120, 120)),
            ("Top Kill:", f"{getattr(most_kills, 'kills', 0)}", (255, 80, 80)),
        ]

        sy = y + 14
        for label, value, color in stats_left:
            label_surf = self.font_tiny.render(label, True, self.text_dim)
            value_surf = self.font_tiny.render(value, True, color)
            screen.blit(label_surf, (col1_x, sy))
            screen.blit(value_surf, (col1_x + 60, sy))
            sy += 13

        # Reproduction section
        repro_header = self.font_tiny.render("REPRODUCTION", True, (100, 200, 100))
        screen.blit(repro_header, (col2_x, y))

        stats_right = [
            ("Births:", f"{total_offspring}", (100, 200, 100)),
            ("Birth Rate:", f"{birth_rate:.2f}/s", (130, 200, 130)),
            ("Mating:", f"{maters} ({maters*100//total}%)", (255, 150, 180)),
            ("Parents:", f"{parents} ({parents*100//total}%)", (150, 200, 150)),
            ("Top Kids:", f"{getattr(most_offspring, 'offspring_count', 0)}", (80, 255, 80)),
        ]

        sy = y + 14
        for label, value, color in stats_right:
            label_surf = self.font_tiny.render(label, True, self.text_dim)
            value_surf = self.font_tiny.render(value, True, color)
            screen.blit(label_surf, (col2_x, sy))
            screen.blit(value_surf, (col2_x + 65, sy))
            sy += 13

        # Separator
        pygame.draw.line(screen, self.border_color, (x + w // 2, y + 10), (x + w // 2, y + 80), 1)

        # Bottom section - records & diversity
        sy = y + 88
        pygame.draw.line(screen, self.border_color, (x, sy), (x + w, sy), 1)
        sy += 6

        # Oldest agent with species color
        oldest_color = self.get_species_color(oldest.species_id)
        oldest_text = self.font_tiny.render(f"Oldest: {oldest.age:.1f}s", True, oldest_color)
        oldest_name = self.font_tiny.render(f"({self.get_species_name(oldest.species_id)[:8]})", True, self.text_dim)
        screen.blit(oldest_text, (x, sy))
        screen.blit(oldest_name, (x + 70, sy))

        # Death rate and diversity
        death_text = self.font_tiny.render(f"Deaths: {death_rate:.2f}/s", True, (255, 150, 150))
        screen.blit(death_text, (col2_x, sy))

        if self.stats_collector.latest:
            sy += 13
            div = self.stats_collector.latest.genetic_diversity
            div_color = (100, 200, 100) if div > 0.5 else (255, 200, 100) if div > 0.3 else (255, 100, 100)
            div_text = self.font_tiny.render(f"Genetic Diversity: {div:.3f}", True, div_color)
            screen.blit(div_text, (x, sy))

    def _draw_species_gender(self, screen, x, y, w, h, live_agents):
        """Draw gender breakdown for each species with mini bar charts."""
        if not live_agents:
            self._draw_no_data(screen, x, y, w, h)
            return

        # Collect species gender data
        species_data = defaultdict(lambda: {'males': 0, 'females': 0})
        for a in live_agents:
            sid = a.species_id
            if getattr(a, 'sex', '') == 'male':
                species_data[sid]['males'] += 1
            else:
                species_data[sid]['females'] += 1

        if not species_data:
            self._draw_no_data(screen, x, y, w, h)
            return

        # Sort by total population
        sorted_species = sorted(species_data.items(),
                               key=lambda item: item[1]['males'] + item[1]['females'],
                               reverse=True)[:8]

        # Calculate layout - 2 rows of 4 species
        cols = 4
        rows_needed = (len(sorted_species) + cols - 1) // cols
        cell_w = (w - 30) // cols
        cell_h = (h - 20) // max(1, rows_needed)

        for idx, (sid, data) in enumerate(sorted_species):
            row = idx // cols
            col = idx % cols

            cx = x + col * cell_w + 10
            cy = y + row * cell_h

            total = data['males'] + data['females']
            male_pct = data['males'] / total if total > 0 else 0
            female_pct = data['females'] / total if total > 0 else 0

            color = self.get_species_color(sid)
            name = self.get_species_name(sid)

            # Species header with shape
            self._draw_shape_indicator(screen, cx + 8, cy + 10, 12, sid)
            name_text = self.font_small.render(name[:10], True, color)
            screen.blit(name_text, (cx + 20, cy + 3))

            # Total count
            count_text = self.font_tiny.render(f"({total})", True, self.text_dim)
            screen.blit(count_text, (cx + 20 + name_text.get_width() + 5, cy + 5))

            # Gender bar
            bar_y = cy + 22
            bar_w = cell_w - 30
            bar_h = 14

            # Background
            pygame.draw.rect(screen, (50, 55, 65), (cx, bar_y, bar_w, bar_h), border_radius=3)

            # Male portion (left)
            male_w = int(bar_w * male_pct)
            if male_w > 0:
                pygame.draw.rect(screen, self.male_color, (cx, bar_y, male_w, bar_h),
                               border_top_left_radius=3, border_bottom_left_radius=3)

            # Female portion (right)
            female_w = int(bar_w * female_pct)
            if female_w > 0:
                pygame.draw.rect(screen, self.female_color, (cx + bar_w - female_w, bar_y, female_w, bar_h),
                               border_top_right_radius=3, border_bottom_right_radius=3)

            # Counts below bar
            male_text = self.font_tiny.render(f"M:{data['males']}", True, self.male_color)
            female_text = self.font_tiny.render(f"F:{data['females']}", True, self.female_color)
            screen.blit(male_text, (cx, bar_y + bar_h + 3))
            screen.blit(female_text, (cx + bar_w - female_text.get_width(), bar_y + bar_h + 3))

            # Ratio indicator
            if total > 0:
                ratio = data['males'] / data['females'] if data['females'] > 0 else float('inf')
                if ratio == float('inf'):
                    ratio_str = "All M"
                elif ratio == 0:
                    ratio_str = "All F"
                else:
                    ratio_str = f"{ratio:.1f}:1"
                ratio_text = self.font_tiny.render(ratio_str, True, self.text_dim)
                screen.blit(ratio_text, (cx + bar_w // 2 - ratio_text.get_width() // 2, bar_y + bar_h + 3))

            # Mini pie chart for this species
            pie_cx = cx + bar_w + 15
            pie_cy = cy + 25
            pie_r = 18

            if total > 0:
                # Male slice
                male_angle = male_pct * 2 * math.pi
                self._draw_pie_slice(screen, pie_cx, pie_cy, pie_r, 0, male_angle, self.male_color)
                self._draw_pie_slice(screen, pie_cx, pie_cy, pie_r, male_angle, 2 * math.pi, self.female_color)

                # Center dot
                pygame.draw.circle(screen, self.card_color, (pie_cx, pie_cy), 6)

        # Legend at bottom
        legend_y = y + h - 18
        pygame.draw.rect(screen, self.male_color, (x, legend_y, 12, 12))
        male_legend = self.font_tiny.render("Male", True, self.text_color)
        screen.blit(male_legend, (x + 16, legend_y))

        pygame.draw.rect(screen, self.female_color, (x + 70, legend_y, 12, 12))
        female_legend = self.font_tiny.render("Female", True, self.text_color)
        screen.blit(female_legend, (x + 86, legend_y))

        # Overall ratio
        total_males = sum(d['males'] for d in species_data.values())
        total_females = sum(d['females'] for d in species_data.values())
        overall_text = self.font_small.render(
            f"Overall: {total_males}M / {total_females}F ({total_males/(total_males+total_females)*100:.0f}%/{total_females/(total_males+total_females)*100:.0f}%)" if total_males + total_females > 0 else "No data",
            True, self.text_color)
        screen.blit(overall_text, (x + w - overall_text.get_width() - 10, legend_y))

    def _draw_grid(self, screen, x, y, w, h, rows, cols, max_y, max_x, y_label="", x_label=""):
        """Draw a graph grid with labels."""
        # Horizontal lines
        for i in range(rows + 1):
            gy = y + (i / rows) * h
            pygame.draw.line(screen, (50, 55, 65), (x, gy), (x + w, gy), 1)
            if y_label or i == 0 or i == rows:
                val = max_y * (1 - i / rows)
                if isinstance(val, float) and val < 10:
                    label = self.font_tiny.render(f"{val:.1f}", True, self.text_dim)
                else:
                    label = self.font_tiny.render(f"{int(val)}", True, self.text_dim)
                screen.blit(label, (x - 30, gy - 5))

        # Vertical lines
        for i in range(cols + 1):
            gx = x + (i / cols) * w
            pygame.draw.line(screen, (50, 55, 65), (gx, y), (gx, y + h), 1)

    def _draw_pie_slice(self, screen, cx, cy, radius, start_angle, end_angle, color):
        """Draw a pie chart slice."""
        points = [(cx, cy)]
        steps = max(2, int((end_angle - start_angle) * 20))
        for i in range(steps + 1):
            angle = start_angle + (i / steps) * (end_angle - start_angle) - math.pi / 2
            points.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
        if len(points) > 2:
            pygame.draw.polygon(screen, color, points)

    def _draw_shape_indicator(self, screen, x, y, size, species_id):
        """Draw species shape indicator."""
        color = self.get_species_color(species_id)
        shape = self.get_species_shape(species_id)

        if shape == 'circle':
            pygame.draw.circle(screen, color, (x, y), size // 2)
        elif shape == 'square':
            pygame.draw.rect(screen, color, (x - size//2, y - size//2, size, size))
        elif shape == 'triangle':
            pts = [(x, y - size//2), (x - size//2, y + size//2), (x + size//2, y + size//2)]
            pygame.draw.polygon(screen, color, pts)
        elif shape == 'diamond':
            pts = [(x, y - size//2), (x + size//2, y), (x, y + size//2), (x - size//2, y)]
            pygame.draw.polygon(screen, color, pts)
        elif shape == 'hexagon':
            pts = [(x + size//2 * math.cos(math.radians(60*i - 30)),
                   y + size//2 * math.sin(math.radians(60*i - 30))) for i in range(6)]
            pygame.draw.polygon(screen, color, pts)
        elif shape == 'parallelogram':
            off = size * 0.25
            pts = [(x - size//2 + off, y - size//2), (x + size//2 + off, y - size//2),
                   (x + size//2 - off, y + size//2), (x - size//2 - off, y + size//2)]
            pygame.draw.polygon(screen, color, pts)
        elif shape == 'pentagon':
            pts = [(x + size//2 * math.cos(math.radians(72*i - 90)),
                   y + size//2 * math.sin(math.radians(72*i - 90))) for i in range(5)]
            pygame.draw.polygon(screen, color, pts)
        elif shape == 'star':
            pts = []
            for i in range(5):
                outer = math.radians(72 * i - 90)
                pts.append((x + size//2 * math.cos(outer), y + size//2 * math.sin(outer)))
                inner = math.radians(72 * i + 36 - 90)
                pts.append((x + size//4 * math.cos(inner), y + size//4 * math.sin(inner)))
            pygame.draw.polygon(screen, color, pts)
        else:
            pygame.draw.circle(screen, color, (x, y), size // 2)

    def _draw_no_data(self, screen, x, y, w, h):
        """Draw no data message."""
        text = self.font_small.render("Collecting data...", True, self.text_dim)
        screen.blit(text, (x + w // 2 - text.get_width() // 2, y + h // 2 - 6))

    def _draw_scrollbar(self, screen, x, y, w, h, content_h):
        """Draw scrollbar."""
        pygame.draw.rect(screen, (40, 45, 55), (x, y, w, h), border_radius=3)

        visible_ratio = h / content_h
        thumb_h = max(30, int(h * visible_ratio))
        scroll_ratio = self.scroll_y / self.max_scroll if self.max_scroll > 0 else 0
        thumb_y = y + int((h - thumb_h) * scroll_ratio)

        pygame.draw.rect(screen, (90, 100, 120), (x, thumb_y, w, thumb_h), border_radius=3)

    def handle_scroll(self, direction):
        self.scroll_y = max(0, min(self.max_scroll, self.scroll_y + direction * 50))

    def handle_mouse_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                self.scroll_y = max(0, self.scroll_y - 50)
            elif event.button == 5:
                self.scroll_y = min(self.max_scroll, self.scroll_y + 50)

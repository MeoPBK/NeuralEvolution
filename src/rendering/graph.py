import pygame
import config


def draw_graph(screen, stats_collector, font):
    """Draw population over time graph at bottom of HUD panel."""
    snapshots = stats_collector.snapshots
    if len(snapshots) < 2:
        return

    # Calculate graph position based on screen size
    screen_width, screen_height = screen.get_size()
    hud_width = config.HUD_WIDTH

    # Position graph at bottom of HUD area
    graph_x = screen_width - hud_width + 10
    graph_y = screen_height - 180
    graph_w = hud_width - 20
    graph_h = 160

    # Background
    graph_rect = pygame.Rect(graph_x, graph_y, graph_w, graph_h)
    pygame.draw.rect(screen, (20, 20, 30), graph_rect)
    pygame.draw.rect(screen, (60, 60, 80), graph_rect, 1)

    # Label
    label = font.render("Population Over Time", True, (150, 150, 180))
    screen.blit(label, (graph_x + 2, graph_y - 14))

    # Find max population for scaling
    max_pop = max(s.agent_count for s in snapshots)
    max_pop = max(max_pop, 1)

    # Use last GRAPH_W points or fewer
    display_snaps = snapshots[-graph_w:]
    n = len(display_snaps)
    if n < 2:
        return

    # Draw total population line
    agent_points = []
    for i, snap in enumerate(display_snaps):
        px = graph_x + int(i * graph_w / max(n - 1, 1))
        agent_y = graph_y + graph_h - int(snap.agent_count / max_pop * (graph_h - 20)) - 10
        agent_points.append((px, agent_y))

    if len(agent_points) > 1:
        pygame.draw.lines(screen, config.GRAPH_AGENT_COLOR, False, agent_points, 2)

    # Draw per-species lines if we have species data
    if hasattr(stats_collector, 'known_species') and stats_collector.known_species:
        species_ids = list(stats_collector.known_species)[:4]  # Limit to 4 species for readability

        for species_id in species_ids:
            # Generate color based on species ID (golden angle distribution)
            hue = (species_id * 137.5) % 360
            h = hue / 360.0
            s, v = 0.7, 0.85

            c = v * s
            x = c * (1 - abs((h * 6) % 2 - 1))
            m = v - c

            if h < 1/6:
                r, g, b = c, x, 0
            elif h < 2/6:
                r, g, b = x, c, 0
            elif h < 3/6:
                r, g, b = 0, c, x
            elif h < 4/6:
                r, g, b = 0, x, c
            elif h < 5/6:
                r, g, b = x, 0, c
            else:
                r, g, b = c, 0, x

            color = (int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))

            species_points = []
            for i, snap in enumerate(display_snaps):
                px = graph_x + int(i * graph_w / max(n - 1, 1))
                species_count = snap.species_counts.get(species_id, 0) if hasattr(snap, 'species_counts') else 0
                py = graph_y + graph_h - int(species_count / max_pop * (graph_h - 20)) - 10
                species_points.append((px, py))

            if len(species_points) > 1:
                pygame.draw.lines(screen, color, False, species_points, 1)

    # Current value in corner
    latest = display_snaps[-1]
    pop_label = font.render(f"Total: {latest.agent_count}", True, config.GRAPH_AGENT_COLOR)
    screen.blit(pop_label, (graph_x + graph_w - 70, graph_y + 3))

    # Show male/female if available
    if hasattr(latest, 'total_males') and hasattr(latest, 'total_females'):
        gender_label = font.render(f"M:{latest.total_males} F:{latest.total_females}", True, (150, 150, 180))
        screen.blit(gender_label, (graph_x + 5, graph_y + graph_h - 15))

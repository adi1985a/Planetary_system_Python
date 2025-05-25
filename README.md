# 🌌🪐 PySolarSim: Gravitational Playground & Black Hole Dynamics 🌠
_A Python and Pygame-based physics simulation of a solar system, featuring real-time gravitational interactions, black hole creation, planet collisions, and time manipulation._

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) <!-- Assuming MIT if not specified -->
[![Python](https://img.shields.io/badge/Python-3.x-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-Graphics%20%26%20Physics-6495ED.svg?logo=pygame)](https://www.pygame.org/)

## 📋 Table of Contents
1.  [Overview](#-overview)
2.  [Key Features](#-key-features)
3.  [Interactive Controls](#-interactive-controls)
4.  [System Requirements](#-system-requirements)
5.  [Installation](#️-installation)
6.  [Running the Simulation](#️-running-the-simulation)
7.  [File Structure (Expected)](#-file-structure-expected)
8.  [Contributing](#-contributing)
9.  [License](#-license)
10. [Author](#-author)

## 📄 Overview

**PySolarSim: Gravitational Playground & Black Hole Dynamics**, developed by Adrian Lesniak, is a physics-based simulation that allows users to explore the interactions within a simplified solar system. Built with **Python** and the **Pygame** library, it features real-time gravitational physics, the ability to dynamically create black holes and observe their impact on celestial bodies, planet collisions, and even simulated time dilation effects. Users can control the simulation speed, adjust black hole properties, and save or load the state of their cosmic experiments.

## ✨ Key Features

*   🌌 **Real-Time Gravitational Physics**: Simulates the gravitational attraction between celestial bodies (planets, stars, black holes) in real-time, influencing their orbits and trajectories.
*   ⚫ **Black Hole Creation & Interactions**:
    *   Users can dynamically create black holes within the simulation space.
    *   Observe how these black holes affect nearby planets and other objects through their immense gravity.
*   💥 **Planet Collisions**: Models and visualizes collisions between planets or other celestial bodies.
*   ⏳ **Time Dilation Effects**: Incorporates a representation of time dilation, likely influenced by proximity to strong gravitational fields (like black holes) or high velocities.
*   💾 **Save/Load Simulation States**:
    *   Allows users to save the current configuration and state of the solar system.
    *   Previously saved states can be loaded to resume or re-examine specific scenarios.
*   ⚙️ **Simulation Speed Control**: Users can adjust the simulation speed (e.g., 0.5x, 1x, 2x, 5x) to observe events at different paces.
*   🎛️ **Black Hole Parameter Adjustment**: Provides controls to modify properties of created black holes, such as their size or mass (which influences their gravitational pull).
*   🔄 **Simulation Reset**: Option to reset the simulation to its initial state or a predefined starting configuration.

## 🕹️ Interactive Controls

*   **Left Mouse Click**: Create a black hole at the cursor's position.
*   **Speed Controls**: UI elements or keyboard shortcuts to adjust simulation speed (e.g., `+` and `-` keys, or buttons for 0.5x, 1x, 2x, 5x).
*   **Black Hole Size Adjustment**: UI elements or keyboard shortcuts to control the size/mass of newly created or selected black holes.
*   **Reset Simulation**: A dedicated button or key to revert the simulation to its default starting conditions.
*   **Save System State**: A button or key to save the current state of all objects in the simulation.
*   **Load System State**: A button or key to load a previously saved simulation state.
*   *(Additional controls for panning, zooming, or selecting objects might also be present).*

## ⚙️ System Requirements

*   **Python**: Python 3.x (e.g., 3.6 or higher recommended).
*   **Pygame**: The Pygame library for graphics, event handling, and windowing.
*   **Operating System**: Any OS that supports Python 3.x and Pygame (e.g., Windows, macOS, Linux).

## 🛠️ Installation

1.  **Install Python 3.x**:
    If you don't have Python installed, download it from [python.org](https://www.python.org/) and install it. Ensure Python is added to your system's PATH.

2.  **Install Pygame**:
    Open your terminal or command prompt and install Pygame using pip:
    ```bash
    pip install pygame
    ```

3.  **Clone or Download the Repository**:
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```
    *(Replace `<repository-url>` and `<repository-directory>` if applicable, or simply download/save `main.py` and any other project files).*

## ▶️ Running the Simulation

1.  Navigate to the project directory in your terminal or command prompt (the one containing `main.py`).
2.  Run the simulation using Python:
    ```bash
    python main.py
    ```
    or if you use the `python3` alias:
    ```bash
    python3 main.py
    ```
3.  The Pygame window should open, and the solar system simulation will begin. Interact with it using the controls outlined above.

## 🗂️ File Structure (Expected)

*   `main.py`: The primary Python script containing the simulation logic, physics calculations, Pygame event loop, rendering, and user interaction handlers.
*   (Potentially) `config.py` or similar: For simulation parameters if not hardcoded in `main.py`.
*   (Potentially) Asset folders: For any sprites, background images, or sound files if used.
*   (Potentially) Save files: Files created when using the "Save System State" feature (e.g., `.json`, `.pkl`, or custom format).
*   `README.md`: This documentation file.

## 📝 Technical Notes

*   **Physics Model**: The accuracy of the simulation depends on the implemented physics model for gravity, collisions, and time dilation. These are likely simplified for a Pygame application but aim to demonstrate the concepts.
*   **Performance**: Real-time physics simulations with many interacting bodies can be computationally intensive. Performance will depend on the number of objects, the complexity of calculations, and the efficiency of the Pygame rendering loop.
*   **User Interface**: The UI for controls (speed, black hole size, save/load) would be implemented using Pygame's drawing and event handling capabilities (e.g., clickable areas, text rendering).
*   **Save/Load Format**: The format for saving and loading simulation states needs to be defined (e.g., JSON, Python's `pickle`, or a custom binary format).

## 🤝 Contributing

Contributions to **PySolarSim** are highly encouraged! If you have ideas for:

*   Adding more types of celestial bodies (e.g., comets, asteroids, nebulae).
*   Implementing more accurate or diverse physics models.
*   Enhancing the visual appeal with better graphics or particle effects.
*   Improving the user interface and controls.
*   Adding educational overlays or information about the simulated phenomena.
*   Optimizing performance for larger simulations.

1.  Fork the repository.
2.  Create a new branch for your feature (`git checkout -b feature/GalaxyGeneration`).
3.  Make your changes to `main.py` and any related files.
4.  Commit your changes (`git commit -m 'Feature: Add procedural galaxy generation'`).
5.  Push to the branch (`git push origin feature/GalaxyGeneration`).
6.  Open a Pull Request.

Please ensure your code is well-commented and follows Python best practices (e.g., PEP 8), including type hints where appropriate.

## 📃 License

This project is licensed under the **MIT License**.
(If you have a `LICENSE` file in your repository, refer to it: `See the LICENSE file for details.`)

## 👤 Author

Simulation concept by **Adrian Lesniak**.
For questions, feedback, or issues, please open an issue on the GitHub repository or contact the repository owner.

---
✨ _Shape the cosmos and witness gravitational wonders in your own Python-powered universe!_

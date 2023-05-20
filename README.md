# Arkanoid Game
An implementation of the classic arcade game Arkanoid in Python using Pygame, with a NEAT AI player.


![Game screenshot](screenshot.png)


## Features
* Player-controlled paddle with keyboard input.
* Ball and brick physics.
* Sound effects.
* AI player using NeuroEvolution of Augmenting Topologies (NEAT).

## Installation
Make sure you have Python 3.x installed and the latest version of pip installed before running these steps.

Clone the project:
```python
git clone https://github.com/yourusername/Arkanoid-Game.git
```
Navigate into the project directory:
```python
cd Arkanoid-Game
```
Create a virtual environment:
```python
python3 -m venv env
```
Activate the virtual environment:
```python
source env/bin/activate  # for macOS/Linux
env\Scripts\activate     # for Windows
```
Install all dependencies:
```python
pip install -r requirements.txt
```
## Usage
You can run the game as a player:
```python 
Ark().main()
```
You can also train the AI:
```python 
run_neat(config)
```
Or you can have the AI play the game:
```python 
test_best_network(config)
```
## License
This project is licensed under the terms of the MIT license.

## To-Do

- [ ] Improve the AI training efficiency.
- [ ] Add more levels to the game.
- [ ] Improve UI and game design.
- [x] Refine and enhance game mechanics 

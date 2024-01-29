# FishFood Game

Welcome to FishFood, a thrilling arcade-style game where your objective is to survive, grow, and score high in an underwater world.

## Game Description

In FishFood, you are a small fish navigating the perils of a vast ocean. Your aim is to eat smaller fish to score points and grow, while strategically avoiding larger predators that threaten your survival.

### Key Features:

- **Dynamic Eating Mechanism**: Eat fish smaller than you to gain points and grow. Collide face-first into another fish to consume it.
- **Size-Based Menu**: A top-left menu indicates which fish you can eat based on your current size.
- **Predators and Power-ups**:
  - Beware of sharks! They can always eat you, except when miniaturized.
  - Seastars grant random power-ups: invincibility or shrinking sharks.
  - Seahorses increase your speed temporarily.
- **Variety of Fish**:
  - Small Red Fish: Worth 1 point, small and bounce off boundaries.
  - Small Green Fish: Worth 2 points, can grow into big green fish.
  - Big Green Fish: Worth 2 points. Predatory if larger than the player.
  - Silver Fish: Worth 3 points, periodically crosses the screen.
  - Rainbow Fish: Changes size and behavior. Predatory when larger than the player.
  - Big Bright Blue Fish: Appears every 50 points and is always predatory.
- **Hazards**: Avoid jellyfish and sea snakes that can slow you down or cause size loss.

### Gameplay Notes:

- Platform Compatibility: Playable on both PC and mobile devices.
- Play on Browser: Available at [https://bradwyatt.itch.io/fishfood](https://bradwyatt.itch.io/fishfood).
- Controls: Simple movement controls (up, left, right, down) on mobile; arrow keys on PC for enhanced gameplay.

## Demo

<p align="center">
  <img src="https://github.com/bradwyatt/Fish-Food/blob/master/Docs/demo.gif?raw=true" width="500" height="400"></img>
</p>

## How To Play

![ScreenShot](/Docs/InfoScreen.PNG)

## Technical Details

- **Programming Language**: The game is developed in Python.



## Installation and Running the Game

### Playing Online on itch.io

FishFood is easily accessible online! Just follow these simple steps to start playing:

1. Visit the game's page on itch.io: [FishFood on itch.io](https://bradwyatt.itch.io/fishfood)
2. Wait for the page and the application to fully load. Then, follow the provided instructions to start playing the game.

### Running Locally on Your PC

If you instead want to run FishFood on your local machine, follow these steps:

#### Prerequisites
Ensure you have Python installed on your PC. FishFood is compatible with Python 3.12.1. You can download Python from [python.org](https://www.python.org/downloads/).

#### Clone the Repository
Clone the FishFood repository from GitHub to your local machine:
```git clone https://github.com/bradwyatt/FishFood.git```

#### Install Dependencies
Navigate to the cloned repository directory and install the required dependencies:
```
cd FishFood
pip install -r requirements.txt
```
This will install all the necessary Python packages listed in `requirements.txt`.

#### Run the Game
Finally, run the game using Python:
```
python FishFood.py
```

Replace `FishFood.py` with the actual name of the main game script.

Now you're all set to enjoy FishFood on your PC!


## Collaboration and Contributions

I warmly welcome contributions to FishFood and am open to collaboration. Whether you have suggestions for improvements, bug fixes, or new features, please feel free to open an issue or submit a pull request on GitHub.

Additionally, I'm eager to collaborate with other developers and enthusiasts. If you're interested in working together to expand features, optimize code, brainstorm new game ideas, or even embark on new projects, I'd be delighted to hear from you. 

For contributions to FishFood:
- Open an issue or submit a pull request on GitHub repository: [Fish-Food](https://github.com/bradwyatt/Fish-Food)

For collaboration and more detailed discussions:
- Contact me at **GitHub**: [bradwyatt](https://github.com/bradwyatt)

Your ideas, skills, and enthusiasm are all greatly appreciated, and I look forward to the potential of working together.

---

Get ready to dive into the competitive world of FishFood!

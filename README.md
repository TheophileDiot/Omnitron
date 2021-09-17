<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/TheophileDiot/Omnitron">
    <img src="omnitron.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Omnitron</h3>

  <p align="center">
    This bot has everything you want in a discord server !
    <br />
    <br />
    <a href="https://github.com/TheophileDiot/Omnitron/issues">Report Bug</a>
    ·
    <a href="https://github.com/TheophileDiot/Omnitron/issues">Request Feature</a>
    ·
    <a href="https://theophilediot.github.io/Omnitron/">Documentation</a>
    <br />
    <a href="https://github.com/TheophileDiot/Omnitron/main/LICENSE"><img alt="License: MIT" src="https://black.readthedocs.io/en/stable/_static/license.svg"></a>
    <a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
  </p>
</p>

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About The Project

### Built With

- [Python](https://www.python.org)
- [discord.py](https://discordpy.readthedocs.io/en/stable/)

<!-- GETTING STARTED -->

## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

- python
- pip

### Installation

1. Clone the repo

   ```sh
   git clone https://github.com/TheophileDiot/Omnitron.git
   ```

2. (Optional) Create a python virtualenv

   ```sh
   python3 -m venv env
   source env/bin/activate
   ```

3. Install the modules packages

   ```sh
   pip install -r requirements.txt
   ```

4. Create a .env file and put all your environment variables in it, variables needed : `BOT_TOKEN`, `FIREBASE_APIKEY`, `FIREBASE_AUTHDOMAIN`, `FIREBASE_DATABASEURL`, `FIREBASE_STORAGEBUCKET`, `FIREBASE_USER_EMAIL`, `FIREBASE_USER_PASSWORD` or put them in the data/constants.py file !

### Launch the bot:

`python bot.py`

### Buildpacks needed for heroku

- `https://github.com/xrisk/heroku-opus.git`
- `https://github.com/heroku/heroku-buildpack-apt`
- `https://github.com/heroku/heroku-buildpack-jvm-common.git`

<!-- ROADMAP -->

## Roadmap

See the [open issues](https://github.com/TheophileDiot/Omnitron/issues) for a list of proposed features (and known issues).

<!-- CONTRIBUTING -->

## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- LICENSE -->

## License

Distributed under the MIT License. See `LICENSE` for more information.

<!-- CONTACT -->

## Contact

Project Link: [https://github.com/TheophileDiot/Omnitron](https://github.com/TheophileDiot/Omnitron)
Email : [theophile.diot900@gmail.com](mailto:theophile.diot900@gmail.com)

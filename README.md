# OCRR Engine

## Overview

The OCRR Engine is a Python-based application designed to handle Optical Character Recognition (OCR) tasks. It manages document processing through a queuing system, leveraging concurrent processing and a MongoDB database for document status management. The engine reads configuration settings from an external file, initializes a logger for activity tracking, and processes documents in an 'IN_PROGRESS' state.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Directory Structure](#directory-structure)
- [Contributing](#contributing)
- [License](#license)

## Features
- **Configuration Management**: Reads paths and settings from a configuration file.
- **Logging**: Comprehensive logging using `OCRRLogger`.
- **Database Integration**: Connects to a MongoDB database to manage document statuses.
- **Queue Management**: Manages documents in an 'IN_PROGRESS' state using a queue.
- **Concurrent Processing**: Utilizes `ThreadPoolExecutor` for concurrent task execution.

## Installation

### Prerequisites
- Python 3.x
- MongoDB
- Required Python packages (listed in `requirements.txt`)

### Steps
1. **Clone the repository**:
    ```bash
    git clone https://github.com/your-repository/ocrr-engine.git
    cd ocrr-engine
    ```

2. **Install the required Python packages**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Configure MongoDB**:
   Ensure MongoDB is running and accessible.

4. **Prepare the Configuration File**:
   Edit the `configuration.ini` file located at `C:\Program Files\OCRR\settings\configuration.ini`.

## Configuration

The `configuration.ini` file should be placed at `C:\Program Files\OCRR\settings\configuration.ini`. This file should include paths for document upload and OCR workspace:

```ini
[Paths]
upload = /path/to/document/upload
workspace = /path/to/ocrr/workspace

**Usage
python ocrr_engine.py


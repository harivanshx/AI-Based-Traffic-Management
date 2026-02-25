# AI-Based Traffic Management System

An intelligent traffic management system that uses YOLOv8 for real-time vehicle detection and dynamically adjusts traffic signal timing based on congestion levels.

The system is optimized for CPU-only execution and does not require GPU acceleration.

For detailed problem statement and system design, see `PROBLEM_STATEMENT.md`.

---

## Overview

This project implements a real-time traffic monitoring and adaptive signal control system. It detects vehicles using a lightweight YOLOv8 model and dynamically allocates green signal duration based on traffic density in four directions (North, South, East, West).

The system is designed to be efficient, modular, and easily extensible.

---

## Key Features

- Real-time vehicle detection using YOLOv8n
- Multi-class detection (cars, buses, trucks, motorcycles)
- Four-direction traffic density analysis
- Adaptive signal timing (15–90 seconds)
- CPU-optimized execution
- Modular architecture
- Live visualization with statistics
- Headless execution support

---

## Traffic Density Classification

| Density Level | Vehicle Count | Green Duration |
|--------------|--------------|----------------|
| LOW          | 0–5          | 15–20 sec      |
| MEDIUM       | 6–15         | 25–35 sec      |
| HIGH         | 16–25        | 40–60 sec      |
| CRITICAL     | 26+          | 60–90 sec      |

---

## System Requirements

- Python 3.8 or higher
- Webcam or traffic video file
- Windows, Linux, or macOS

---

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd AI-Based-Traffic-Management-System

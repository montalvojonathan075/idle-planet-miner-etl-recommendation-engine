# Idle Planet Miner ETL Recommendation Engine

## Executive Summary
This project is a Python-based ETL and recommendation engine built to turn raw operational data into actionable business insight. It ingests source data, cleans and validates it, derives performance metrics, evaluates available options, and ranks the most valuable actions using ROI and breakeven logic.

The project demonstrates an end-to-end analytical workflow: collecting raw operational data, cleaning and standardizing it, validating data quality, creating performance metrics, applying business rules, and generating prioritized recommendations based on measurable value. It highlights the ability to transform fragmented source data into decision-ready insight and support business actions with clear, defensible analysis.

---

## Project Highlights
This project demonstrates a strong data-to-decision workflow, combining ETL processes, business logic, and analytical scoring to identify the most valuable next action based on measurable outcomes.

The work reflects core analytical capabilities in:
- ETL pipeline development
- Data cleaning and standardization
- Data validation and quality control
- KPI and metric creation
- Business-rule implementation
- Recommendation logic and prioritization
- Decision support through analytical scoring

---

## Business Problem
The challenge is to determine which available action delivers the greatest value when multiple options compete for attention. This project evaluates each alternative against profitability, cost efficiency, and investment recovery time to identify the most effective decision.

The recommendation engine applies objective, data-driven logic to support action prioritization rather than relying on intuition alone.

---

## Solution
The project uses a complete ETL workflow to transform raw data into structured, prioritized recommendations.

### ETL Process
1. Extract raw planet and ore data
2. Clean and standardize source files
3. Validate schema and enforce business rules
4. Calculate planet value and operational metrics
5. Generate all valid action options
6. Estimate projected gains and action costs
7. Score alternatives using ROI, breakeven, and hybrid logic
8. Rank and surface the highest-value recommendations

---

## Recommendation Logic
The engine evaluates actions using several business-focused strategies:

### Best ROI
Prioritizes the highest return relative to the investment cost.

### Best Hybrid
Balances profitability with sustainable long-term value.

### Best Breakeven
Focuses on the fastest cost recovery.

### Lowest Cost
Targets the most affordable options while maintaining progress.

This logic reflects an understanding of how businesses often need to balance speed, efficiency, and value rather than maximizing one metric in isolation.

---

## ETL Workflow

Raw Data
  ↓
Load & Clean
  ↓
Validation
  ↓
Planet Worth Calculations
  ↓
Player State Processing
  ↓
Planet Metrics
  ↓
Possible Actions
  ↓
Action Gains
  ↓
Action Scoring
  ↓
Decision Engine
  ↓
Recommendations

---

## Project Structure

```text
ETL Scripts/
├── load_and_clean.py
├── planet_worth.py
├── planet_levels.py
├── planet_metrics.py
├── possible_actions.py
├── action_gains.py
├── action_scores.py
├── decision_engine.py
├── questionnaire.py
├── Main.py

Raw Data/
├── Source files

DataFrames/
├── Generated ETL outputs
```

---

## Core Components

### load_and_clean.py
Loads raw source data, standardizes values, validates quality, and prepares clean datasets for analysis.

### planet_worth.py
Calculates the value of each planet based on ore composition and supporting factors.

### planet_levels.py
Tracks the progression and persistent state of the system.

### planet_metrics.py
Computes operational metrics such as:
- Mining rate
- Cargo capacity
- Ship speed
- Trip time
- Deposit rate
- Operational efficiency

### possible_actions.py
Generates valid action options including:
- Planet unlocks
- Mining upgrades
- Cargo upgrades
- Speed upgrades

### action_gains.py
Measures projected gains and costs to identify opportunities with meaningful value.

### action_scores.py
Applies analytical scoring using:
- ROI
- Breakeven timing
- Hybrid scoring

### decision_engine.py
Chooses the highest-ranked recommendations and turns scoring results into actionable decisions.

---

## Example Output
The system produces prioritized recommendations such as:

```text
Best ROI: Unlock Planet 2
Best Hybrid: Mining Upgrade Planet 1
Best Breakeven: Cargo Upgrade Planet 1
Lowest Cost: Speed Upgrade Planet 1
```

This output demonstrates how raw data can be converted into a clear, decision-support recommendation framework.

---

## Technical Skills Demonstrated
- Python development
- pandas data processing
- ETL workflow design
- Data validation and cleaning
- Business rule implementation
- KPI and metric creation
- ROI and breakeven analysis
- Recommendation engine logic
- Workflow automation

---

## How to Run
From the project root, run:

```bash
python "ETL Scripts/Main.py"
```

The application will:
- execute the ETL workflow
- generate ranked recommendations
- present the most valuable actions
- update outcomes based on changing data inputs

---

## Portfolio Relevance
This project was designed to demonstrate the kind of analytical work employers expect from a junior data analyst: turning raw information into structured, trustworthy, decision-ready insight.

Although the scenario is built around a game environment, the underlying workflow mirrors real-world problem solving in operations, planning, optimization, and performance analysis. It demonstrates the ability to create a complete data-to-decision pipeline that is both technically sound and business relevant.

---

## Final Note
This project reflects a complete analytical workflow, from raw data collection to metric creation, business-rule analysis, and recommendation generation. It highlights the ability to work with imperfect data, apply logic to transform it into useful insight, and produce decisions that are grounded in measurable value.

# Student Performance AI Predictor

## Project Overview

This project explores how quantitative methods and machine learning can be used to analyse student academic performance and identify students who may be at risk of failing.

The system uses longitudinal student data including academic scores, attendance, and homework completion.

The project is developed progressively from descriptive analytics to predictive modelling and machine learning.

## Dataset

The prototype uses a synthetic dataset containing 50 students studying three subjects:

- Mathematics
- English
- Biology

The dataset contains the following variables:

- `student_id`
- `date`
- `week`
- `subject`
- `score_percent`
- `attendance`
- `homework_completed`

The dataset is synthetic and contains no real student information.

Attendance patterns were synthetically constructed to create an association with academic performance for modelling and demonstration purposes. Therefore, relationships identified in this dataset should not be interpreted as causal evidence.

## Level 1 — Descriptive Analytics

The first stage focuses on understanding and visualising student performance.

Functions include:

- Tracking weekly student scores
- Visualising individual student performance
- Comparing performance across subjects
- Identifying improving or declining academic trends

## Level 2 — Quantitative Prediction

### Linear Extrapolation

Recent historical scores are used to extrapolate a student's expected Week 21 academic performance.

### Multiple Linear Regression

The prediction model is extended to incorporate:

- Week
- Attendance
- Homework completion

The model estimates future Mathematics performance using both academic and engagement information.

## Level 2.5 — Failure Risk Classification

A logistic regression model is used to estimate the probability that a student will fail Mathematics.

Failure is currently defined as:

`Mathematics score < 40%`

Predictive features include:

- Recent average score
- Most recent score
- Score trend
- Attendance rate
- Homework completion rate
- Score volatility

The model therefore produces a probability of failure rather than only a predicted score.

## Level 3 — Machine Learning

The next stage will develop a Deep Neural Network (DNN) to predict student failure risk.

The DNN will be evaluated against the logistic regression baseline to determine whether increased model complexity provides meaningful predictive improvement.

## System Objective

The long-term objective is to develop a student early-warning information system:

**Student Data → Data Processing → Predictive Model → Failure Risk → Teacher Dashboard → Early Intervention**

The project aims to demonstrate how quantitative modelling, machine learning, and information systems can be integrated to support data-informed educational decision-making.

## Technologies

- Python
- pandas
- NumPy
- Matplotlib
- scikit-learn

## Disclaimer

This project is a prototype developed using synthetic data for educational and research purposes.

The model outputs should not be interpreted as real educational assessments or used for real student decision-making.

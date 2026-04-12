
# Implement average cost policy

## TL;DR
Define how cost basis is calculated for holdings derived from transactions.

## Type
Core Feature

## Priority
High

## Effort
Medium

## Decision
Use weighted average cost for MVP.

Example:

BUY 10 @ 100  
BUY 10 @ 200  

avg_cost = 150

## Requirements
- Maintain avg_cost for each holding
- Recalculate after every BUY
- SELL should not change avg cost of remaining shares

## Acceptance criteria
- avg cost updates correctly after buys
- sells reduce quantity but keep cost basis consistent

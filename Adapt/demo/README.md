# ADAPT judging demonstration

The product demo is offline-first and uses the **actual** `AdaptiveTutor`. Demo inputs are scripted; displayed strategies are not.

## Start

```bash
python -m app
```

Open [http://127.0.0.1:8765](http://127.0.0.1:8765).

## Commands

```bash
python demo/run_demo.py
python demo/run_competition_demo.py
```

`run_competition_demo.py` prints the guided path and the counterfactual, and checks that displayed decisions equal engine decisions.

## Live path

1. Landing: promise + How it adapts chain.
2. **Watch the demo** or **Try ADAPT**.
3. Leave **Research view** on.
4. After a submit, read the adaptation card. It is generated from the trace.
5. **Counterfactual**: same start, two real engine runs.
6. Architecture / Evidence / Limitations pages are in the header.

Demo scenarios are labeled **DEMO SCENARIO**. They are not human study results.

Phase 5 human learning evaluation: INCONCLUSIVE (n=0).

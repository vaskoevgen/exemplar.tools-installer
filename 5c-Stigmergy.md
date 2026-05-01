```
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-app-test2 (feature/howto-next-iteration)> stigmergy init
stigmergy init

  env      ANTHROPIC_API_KEY set

  What should stigmergy monitor? [Monitor engineering signals for the platform team]: 

--- Sources ---
  Enable GitHub? [Y/n]: y
  No repos/ directory found. Default: 16 repos
  Use default repos? [Y/n]: y
  GitHub mode (live/mock) [live]: mock
  Enable Linear? [Y/n]: n
  Enable Grafana? [y/N]: N

--- LLM ---
  ANTHROPIC_API_KEY detected — defaulting to anthropic provider
  LLM provider (stub/anthropic) [anthropic]: stub
  Model [claude-haiku-4-5-20251001]: 

--- Budget ---
  Daily cap (USD) [5.00]: 
  Hourly cap (USD) [1.00]: 

Config written to .stigmergy/config.yaml
  16 GitHub repos, 0 Linear teams, provider=stub
Run `stigmergy run --once` to process signals.
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-app-test2 (feature/howto-next-iteration)> stigmergy run --once
stigmergy run --once (mesh)

Mesh initialized: 3 workers, 2 agents, 16 repos, 0 packages, 0 edges

Connecting github  (mock)...
Backfilling github since 2026-03-16...
  github: 7 signals fetched

Routing 7 signals through mesh...
  ----------------------------------------------------------------------
  Caucus: seeded 3 workers with 6 signals
  Caucus suggests 2 workers
  [1/7] $0.00 spent | ~0m remaining   
  [GITHUB]  acme-org/backend  @alice.chen
  PR #487: Fix cache invalidation race condition. Changes src/cache/invalidation.t...
    hop 0  18f2d0b1 (looks/sync/race     )  [##........] 0.285  ACCEPT  rag_indexed
  [2/7] $0.00 spent | ~0m remaining   
  [GITHUB]  acme-org/backend  @bob.martinez
  Looks like this duplicates the fix already done in PR #480. We should close one ...
    hop 0  18f2d0b1 (looks/sync/race     )  [##........] 0.204  ACCEPT  context_summarized
    >> PARALLEL ACTIVITY  61%  @bob.martinez and @alice.chen in same signal space (spectral similarity 100%)
  [3/7] $0.00 spent | ~0m remaining     [GITHUB] rag_indexed          1hop/1accept  acme-org/backend  @carol.park  Review (CHANGES_REQUESTED): The retry backoff should cap at ...
  [4/7] $0.00 spent | ~0m remaining     [GITHUB] rag_indexed          1hop/1accept  acme-org/sync-service  @dave.kim  PR #488: Add backpressure handling with configurable queue d...
  [5/7] $0.00 spent | ~0m remaining       >> PARALLEL ACTIVITY  61%  @bob.martinez and @carol.park in same signal space (spectral similarity 100%)
  [6/7] $0.00 spent | ~0m remaining       >> PARALLEL ACTIVITY  61%  @github-actions and @dave.kim in same signal space (spectral similarity 100%)
  [7/7] $0.00 spent | ~0m remaining     ... 3 suppressed (2 github:context_summarized, 1 github:rag_indexed)
                                                            
Mesh Topology
  ----------------------------------------------------------------------
  Worker         Fullness  Threshold  Signals     Mode Label
  ----------------------------------------------------------------------
  18f2d0b1              2%      0.060        3        - looks/sync/race
  af7d7c3f              2%      0.054        2        - booking/test/race
  ba622a0c              2%      0.054        2        - queue/rate/main
  ----------------------------------------------------------------------

  Budget: $0.0000/$5.00 daily (0%) | $0.0000/$1.00 hourly (0%)

Mesh Session Summary
  ----------------------------------------------------------------------
  Signals processed:  7
  Accepted:           7
  Duplicates:         0
  Windows scanned:    1
  Deepest timestamp:  2026-03-16T16:57:31.155560+00:00
  Stop reason:        complete
  ----------------------------------------------------------------------
  Workers:            3
  Avg fullness:       2%
  ----------------------------------------------------------------------
  Total cost:         $0.0000

  ----------------------------------------------------------------------
  Policy: 7 traces, 0 interventions

Agent Intelligence Report
  ----------------------------------------------------------------------
  0/2 agents have LLM (2 MISSING)
  Correlator (reflect):  0 LLM calls, 14 mechanical, 0 non-batch skipped
  Surfacer (evaluate):   0 LLM calls, 0 mechanical
  WARNING: 2 agents running without LLM — mechanical heuristics producing noise
    agent c922c762: 7 mechanical reflects, 0 mechanical evals
    agent 1742b60b: 7 mechanical reflects, 0 mechanical evals
  ----------------------------------------------------------------------


Key Findings
  ----------------------------------------------------------------------

  61%  S(f)=0.045 [d_bridge=0.50, c_entity=0.30, r_coupling=0.40, gamma=0.75]
    @bob.martinez and @alice.chen in same signal space (spectral similarity 100%)

  61%  S(f)=0.045 [d_bridge=0.50, c_entity=0.30, r_coupling=0.40, gamma=0.75]
    @bob.martinez and @carol.park in same signal space (spectral similarity 100%)

  61%  S(f)=0.045 [d_bridge=0.50, c_entity=0.30, r_coupling=0.40, gamma=0.75]
    @github-actions and @dave.kim in same signal space (spectral similarity 100%)
  ----------------------------------------------------------------------

Insight Funnel
  Raw insights produced:   6
  After agent dedup:       3  (-3)
  After display dedup:     3  (-0)
  Collapse ratio:          3/6 (50% survived)


Phase 2: Cross-Signal Corroboration
  ----------------------------------------------------------------------
  Findings submitted:  3
  Workers consulted:   2 (0 LLM, 2 mechanical)
  Quorum threshold:    2 workers
  Quorum achieved:     0

  3 findings did not achieve quorum (insufficient independent corroboration)
  ----------------------------------------------------------------------

  Persisted 3 insights to .stigmergy/insights.jsonl (run 38d9dae7)

Portfolio Risk Clusters
  ----------------------------------------------------------------------
  1 cluster(s) detected, 0 escalated

  Compound S(f)=0.072  (max individual=0.045)  3 findings
    shared terms: 100%, @bob.martinez, same, signal, similarity, space, spectral
    shared channels: acme-org/backend, acme-org/pricing, acme-org/sync-service
    S(f)=0.045  @bob.martinez and @alice.chen in same signal space (spectral similarity 100%)
    S(f)=0.045  @bob.martinez and @carol.park in same signal space (spectral similarity 100%)
    S(f)=0.045  @github-actions and @dave.kim in same signal space (spectral similarity 100%)
  ----------------------------------------------------------------------


Normalized Deviance Indicators
  ----------------------------------------------------------------------
  [compression] index=0.24  hedging=0.00  passive=0.00  nominalization=0.60  specificity=0.40
    LD=0.765 SE=5.90
    1 channel(s) born caged (initial compression >= 0.3):
      acme-org/backend: initial=0.30 current=0.24 delta=-0.06
  ----------------------------------------------------------------------


Finding Registry
  ----------------------------------------------------------------------
  Total findings: 3  (3 active, 0 deferred, 0 normalized, 0 acknowledged)
  ----------------------------------------------------------------------


Identity Resolution
  ----------------------------------------------------------------------
  Known identities:     0
  Unresolved:           3
  Resolution rate:      0%

  Top unresolved identifiers:
    alice.chen
    bob.martinez
    carol.park
  Persisted corroboration results to .stigmergy/corroboration.json
  Run archived to .stigmergy/runs/20260415_165732
(.venv) yevhenvasko@Yevhens-MacBook-Pro ~/s/e/todo-app-test2 (feature/howto-next-iteration)> stigmergy run --once --live
stigmergy run --once (mesh)

  Loaded dedup index: 7 fingerprints from previous run
Mesh initialized: 3 workers, 2 agents, 16 repos, 0 packages, 0 edges

Connecting github  (mock)...
Backfilling github since 2026-04-15...
  github: 7 signals fetched

Routing 7 signals through mesh...
  ----------------------------------------------------------------------
  Caucus: seeded 3 workers with 7 signals
  Caucus suggests 4 workers
  [1/7] $0.00 spent | ~0m remaining   
  [GITHUB]  acme-org/backend  @alice.chen
  PR #487: Fix cache invalidation race condition. Changes src/cache/invalidation.t...
  [2/7] $0.00 spent | ~0m remaining     [GITHUB] duplicate            0hop/0accept  acme-org/backend  @bob.martinez  Looks like this duplicates the fix already done in PR #480. ...
  [3/7] $0.00 spent | ~0m remaining     [GITHUB] duplicate            0hop/0accept  acme-org/backend  @carol.park  Review (CHANGES_REQUESTED): The retry backoff should cap at ...
  [7/7] $0.00 spent | ~0m remaining     ... 4 suppressed (4 github:duplicate)
                                                            
Mesh Topology
  ----------------------------------------------------------------------
  Worker         Fullness  Threshold  Signals     Mode Label
  ----------------------------------------------------------------------
  18f2d0b1              0%      0.043        3        - backoff/invalidation/src/cache/invalidation.ts
  af7d7c3f              0%      0.043        2        - missing/support/backoff
  ba622a0c              0%      0.043        2        - depth/revenue/queue
  ----------------------------------------------------------------------

  Budget: $0.0000/$5.00 daily (0%) | $0.0000/$1.00 hourly (0%)

Mesh Session Summary
  ----------------------------------------------------------------------
  Signals processed:  7
  Accepted:           0
  Duplicates:         7
  Windows scanned:    1
  Deepest timestamp:  2026-04-15T16:57:32.090862+00:00
  Stop reason:        complete
  ----------------------------------------------------------------------
  Workers:            3
  Avg fullness:       0%
  ----------------------------------------------------------------------
  Total cost:         $0.0000

  ----------------------------------------------------------------------
  Policy: 9 traces, 0 interventions

Agent Intelligence Report
  ----------------------------------------------------------------------
  0/2 agents have LLM (2 MISSING)
  Correlator (reflect):  0 LLM calls, 14 mechanical, 0 non-batch skipped
  Surfacer (evaluate):   0 LLM calls, 0 mechanical
  WARNING: 2 agents running without LLM — mechanical heuristics producing noise
    agent c922c762: 7 mechanical reflects, 0 mechanical evals
    agent 1742b60b: 7 mechanical reflects, 0 mechanical evals
  ----------------------------------------------------------------------


Normalized Deviance Indicators
  ----------------------------------------------------------------------
  [compression] index=0.24  hedging=0.00  passive=0.00  nominalization=0.60  specificity=0.40
    LD=0.765 SE=5.90
    1 channel(s) born caged (initial compression >= 0.3):
      acme-org/backend: initial=0.30 current=0.24 delta=-0.06
  ----------------------------------------------------------------------


Finding Registry
  ----------------------------------------------------------------------
  Total findings: 3  (3 active, 0 deferred, 0 normalized, 0 acknowledged)
  ----------------------------------------------------------------------

  Run archived to .stigmergy/runs/20260415_170201
```
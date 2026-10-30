# MQ04 / EP44 source-depth-v2

Original identity: `kafka-send-confirmation`, “Kafka发送确认：消息发出后，怎样才算发送成功？”. Existing three-aspect covers remain published; no cover image is copied or regenerated here. This revision independently produces new narration, animation and article. Historical source, audio, QA, manifests and published media remain separate.

Kafka/Java4.4.0 commit `1156b2752aaa28eafc0b4c4d387e63356793268d`; full original bytes, GET evidence and hashes are in sources. Read research.md / implementation-map.json for exact permanent lines and claim boundaries. model.py is a finite teaching trace with82 assertions. experiments/run-probe.py directly compiles unmodified official ProducerStateEntry/BatchMetadata and executes15 unit-fixture checks; it does not run Broker/network or ProducerStateManager. This difference is explicit in the article and research.

Run from repo root, with `D=episodes-codex/kafka-send-confirmation/revisions/source-depth-v2`:

```sh
npm ci --prefix "$D/remotion" --no-audit --no-fund
python3 "$D/model.py"
python3 "$D/experiments/run-probe.py"
node "$D/check-references.mjs" --sources "$D"
npm --prefix "$D/remotion" run check:types
python3 episodes-codex/_shared/check_sentence_episode.py "$D"
python3 episodes/_shared/label_onset_strict.py --dir "$D" --out "$D/onset-report.txt"
```

Voice uses unmodified shared prep/gen/build and measured sentence assembly. All30 selected-a takes are newly generated for this revision. build-first.log and voice/selected-signal-review.json record acoustic tail/silence checks; no ASR or full semantic listening is claimed. To intentionally rebuild during production, run local prepare.py, then shared voice tools with `--dir "$D"`, then local assemble.py and shared place_v2.py `--mode whole`. Do not rebuild after freeze merely to validate historical bytes.

For dynamic preflight, from `$D/remotion` run `node scripts/self-preview.mjs`; it generates actual PNGs and six continuous short clips with true no-subtitle props, captures source identities, and rejects changed inputs during its run. Studio is available on4344 during production. qa/self-preview/report.json is provisional generated evidence until actual images/clips are reviewed. It is not a formal whole-body render or final acceptance.

article-figure-plan.json fixes exact integer frames and seconds before encoding. Root extracts those JPEGs from the real formal limited-BT709 MP4 and converts pixels to full-BT601. Active Figure components point to those planned images; they do not exist until root's formal extraction.

The local checker explicitly passes the original slug to the unmodified shared checkSources API because the revision directory basename differs. It does not alter references.episode or relax checks. freeze-inputs.json adds actual style/background/adapter/model/source/experiment/figure dependencies and root's font environment ledger. Original shared checker and appendix engines remain frozen by freeze.py.

Root's unified release gate is required before these production-mutating commands:

```sh
python3 "$D/freeze.py"
python3 "$D/render.py" "$D"
python3 "$D/render.py" "$D" --verify
python3 "$D/verify.py" --final
```

Default path uses the local real-BT709 normalization, shared BGM mix and Kafka palette title-author bibliography, producing body5262 + bibliography150 = final5412 frames /180.4 seconds. No output media/receipt is included in the pre-encoding source manifest. No site/git/publication action belongs to this revision worker.

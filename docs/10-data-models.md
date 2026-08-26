# 10 — Data Models

These are the canonical shapes passed through the Core and across the API to all four platforms. **Every doctrinal field carries its governing `(chapter, verse)` citation** — this is the verse-citation contract encoded in the data, not just the UI.

## 1. Verse
```json
{
  "chapter": 19,
  "verse": 1,
  "sanskrit_ref": "Brihat Jataka 19.1",
  "translation_text": "A person born with the Sun in Aries will have ...",
  "keywords": ["sun", "aries", "appearance"]
}
```

## 2. Graha (planet state)
```json
{
  "name": "Mars",
  "longitude_deg": 142.3,
  "sign": "Leo",
  "sign_lord": "Sun",
  "nakshatra": "Purva Phalguni",
  "nakshatra_lord": "Venus",
  "dignity": "own_sign | exalted | debilitated | moolatrikona | neutral",
  "retrograde": false,
  "bhava": 4,
  "vargas": { "D9": "Libra", "D10": "Scorpio" },
  "citation": { "chapter": 3, "verse": 0 }
}
```

## 3. Rasi / Lagna
```json
{
  "lagna_sign": "Cancer",
  "lagna_longitude_deg": 101.2,
  "houses": [ { "index":1,"sign":"Cancer" }, ... ],
  "ayanamsa": "Lahiri",
  "ayanamsa_value": 24.1,
  "citation": { "chapter": 2, "verse": 0 }
}
```

## 4. Yoga (detected, deterministic)
```json
{
  "yoga_id": "raja_yoga_lord_exchange_12_3",
  "yoga_name": "Raja Yoga (lord exchange)",
  "classification": "strength",
  "condition_matched": { "planets":["Mars","Sun"], "rule_ref":"rule#..." },
  "effect_summary": "Sovereignty/leadership tendency",
  "citation": { "chapter": 12, "verse": 1 },
  "rulebase_version": "2026.07"
}
```

## 5. Dasa timeline
```json
{
  "system": "Vimshottari",
  "periods": [
    { "lord":"Venus", "start":"1990-03-12","end":"2007-03-12",
      "antardasas":[ { "lord":"Venus","start":"...","end":"..."}, ... ],
      "citation": { "chapter":9, "verse":0 } }
  ]
}
```

## 6. Ashtakavarga
```json
{
  "planet": "Sun",
  "bindu_by_house": { "1":1,"2":1,"4":1,"7":0,"8":1,"9":1,"10":1,"11":1 },
  "total_bindus": 7,
  "citation": { "chapter":10, "verse":1 }
}
```

## 7. ChartFactBundle (the core output)
```json
{
  "birth": { "datetime":"1990-01-01T06:30:00+05:30","lat":13.08,"lng":80.27,"place":"Chennai" },
  "lagna": { ... },
  "grahas": [ { ... } ],
  "nakshatra": "Ashlesha",
  "detected_yogas": [ { ... } ],
  "dasa_timeline": { ... },
  "ashtakavarga": { ... },
  "provenance": { "computation_version":"1.0","rulebase_version":"2026.07",
                  "verse_store_version":"2026.07","verification_passed":true }
}
```

## 8. Reading (rendered, served)
```json
{
  "reading_id": "uuid",
  "feature": "mirror",
  "sections": [ { "id":"strengths","title":"Your strengths","body":"...","claims":[...] } ],
  "citations": [ { "claim_text":"...","chapter":19,"verse":1 } ],
  "provenance": { ... },
  "language": "en",
  "altitude": "child | scholar",
  "tone_gate_passed": true,
  "citation_check_passed": true,
  "ethics_check_passed": true
}
```

## 9. BirthDataVault (user-owned)
```json
{
  "user_id": "uuid",
  "birth_records": [ { "id":"rec1","datetime":"...","lat":13.08,"lng":80.27,"place":"Chennai",
                       "label":"Self","encrypted":true } ],
  "deletable": true,
  "used_for_training": false,
  "sold": false
}
```

## 10. RectificationSession
```json
{
  "session_id":"uuid",
  "partial_birth": { "date":"1990-01-01","place":"Chennai","time_window":["04:00","08:00"] },
  "event_anchors":[ { "date":"2015-06-02","nature":"marriage" } ],
  "candidate_times":[ { "datetime":"...","score":0.82,"confidence_band":"medium" } ],
  "selected": { "datetime":"...","confidence_band":"medium","band_minutes":90 },
  "citations":[ { "chapter":26,"verse":0 } ]
}
```

---

*These shapes are the contract between the Core, the API, and all four platform shells. Changing a shape requires updating every consumer and bumping the provenance version.*
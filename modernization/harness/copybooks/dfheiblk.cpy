      ******************************************************************
      *                                                                *
      *  DFHEIBLK - EXEC Interface Block surrogate                     *
      *                                                                *
      *  Milestone note: modernization/harness/translate.py,           *
      *  modernization/harness/driver.cbl and the generated tree       *
      *  modernization/harness/build/ are planned artifacts and are    *
      *  not present in the tree at this milestone; every statement    *
      *  below about the harness or about a translated program is      *
      *  the planned contract.                                         *
      *                                                                *
      *  Declares the five EXEC Interface Block fields that the        *
      *  translated Policy-Issue chain references without declaring:   *
      *  EIBTRNID, EIBTRMID, EIBTASKN, EIBCALEN and EIBRESP2. On CICS  *
      *  the translator supplies these names. Here they are ordinary   *
      *  data items in one EXTERNAL group, and every compilation unit  *
      *  that COPYs this member addresses the same storage.            *
      *                                                                *
      *  To be COPYed by the translated LGAPOL01, LGAPDB01 and         *
      *  LGAPVS01 and by the harness driver. translate.py is to copy   *
      *  this member verbatim into the generated build tree; it is     *
      *  never preprocessed in place.                                  *
      *                                                                *
      *  No item is initialised in this member. The harness driver     *
      *  will seed all five procedurally before it calls the chain,    *
      *  and the translated programs will refresh EIBCALEN before      *
      *  each CALL.                                                    *
      *                                                                *
      *  Rationale is to be recorded in                                *
      *  modernization/docs/decision-log.md (planned deliverable; not  *
      *  present at this milestone), rows: EIB surrogate storage       *
      *  scope; EIBCALEN binary representation.                        *
      *                                                                *
      *  Harness topology:                                             *
      *  Figure 5 — Validation Harness Control Flow                  *
      *  in modernization/docs/architecture.md.                        *
      *                                                                *
      ******************************************************************
      *----------------------------------------------------------------*
      * EXEC Interface Block surrogate                                 *
      *----------------------------------------------------------------*
       01  DFHEIBLK-SURROGATE EXTERNAL.
      *
      * EIBTRNID - identifier of the running CICS transaction.
      *   Referenced at base/src/lgapol01.cbl:88 and
      *   base/src/lgapdb01.cbl:151.
      *   Receiver WS-TRANSID PIC X(4) at base/src/lgapol01.cbl:28
      *   and base/src/lgapdb01.cbl:28.
           03 EIBTRNID                 PIC X(4).
      *
      * EIBTRMID - identifier of the terminal owning the transaction.
      *   Referenced at base/src/lgapol01.cbl:89 and
      *   base/src/lgapdb01.cbl:152.
      *   Receiver WS-TERMID PIC X(4) at base/src/lgapol01.cbl:29
      *   and base/src/lgapdb01.cbl:29.
           03 EIBTRMID                 PIC X(4).
      *
      * EIBTASKN - number of the running CICS task.
      *   Referenced at base/src/lgapol01.cbl:90 and
      *   base/src/lgapdb01.cbl:153.
      *   Receiver WS-TASKNUM PIC 9(7) at base/src/lgapol01.cbl:30
      *   and base/src/lgapdb01.cbl:30.
           03 EIBTASKN                 PIC 9(7).
      *
      * EIBCALEN - length in bytes of the COMMAREA addressed by the
      *   running program. The harness holds 32500 for the whole
      *   chain, matching LENGTH(32500) at
      *   base/src/lgapol01.cbl:121-124 and
      *   base/src/lgapdb01.cbl:243-246.
      *   Referenced at base/src/lgapol01.cbl:91, 98, 113, 154, 155
      *   and 156; base/src/lgapdb01.cbl:154, 165, 210, 339, 580,
      *   581 and 582; base/src/lgapvs01.cbl:97, 173, 174 and 175.
      *   It gates the zero-length ABEND at
      *   base/src/lgapol01.cbl:98 and base/src/lgapdb01.cbl:165;
      *   gates the return code 98 short-COMMAREA exit at
      *   base/src/lgapol01.cbl:113 and base/src/lgapdb01.cbl:210;
      *   bounds the reference modifications at
      *   base/src/lgapol01.cbl:156, base/src/lgapdb01.cbl:582 and
      *   base/src/lgapvs01.cbl:175; and is the minuend of the
      *   endowment VARCHAR length calculation at
      *   base/src/lgapdb01.cbl:339-340.
      *   It is copied into the PIC S9(4) COMP locals of the chain:
      *   WS-CALEN at base/src/lgapol01.cbl:33 and
      *   base/src/lgapdb01.cbl:33; WS-Commarea-Len at
      *   base/src/lgapvs01.cbl:23.
      *   See planned decision-log row: EIBCALEN binary representation.
           03 EIBCALEN                 PIC S9(4) COMP-5.
      *
      * EIBRESP2 - secondary response code of the most recent CICS
      *   command. Referenced once, at base/src/lgapvs01.cbl:143,
      *   on the KSDSPOLY write error path.
      *   Receiver WS-RESP2 PIC S9(8) COMP at
      *   base/src/lgapvs01.cbl:19.
      *   The translated chain will read this item and never write it.
           03 EIBRESP2                 PIC S9(8) COMP.
      *----------------------------------------------------------------*

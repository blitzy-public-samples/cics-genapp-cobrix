      ******************************************************************
      *                                                                *
      *                       CICS-WRITE                               *
      *                                                                *
      *   VSAM write emulation for the GnuCOBOL validation harness     *
      *                                                                *
      ******************************************************************
      *
      * Emulates the one CICS write command of the Policy-Issue chain,
      * records the six operands that command supplied in the shared
      * harness capture state and returns either the normal response
      * condition or the response HC-INJECT-VSAM-RESP selects.
      *
      * Source construct : Write File('KSDSPOLY') command
      *                    base/src/lgapvs01.cbl:135-141
      * File operand     : literal 'KSDSPOLY'
      *                    base/src/lgapvs01.cbl:135
      * Record operand   : WF-Policy-Info, 64 bytes
      *                    base/src/lgapvs01.cbl:25-30
      * Length operand   : literal 64
      *                    base/src/lgapvs01.cbl:137
      * Key operand      : WF-Policy-Key, 21 bytes
      *                    base/src/lgapvs01.cbl:26-29
      * KeyLength operand: literal 21
      *                    base/src/lgapvs01.cbl:139
      * Response operand : WS-RESP
      *                    base/src/lgapvs01.cbl:18
      * Target module    : CICS-WRITE
      *
      * Harness status: modernization/harness/translate.py,
      * modernization/harness/driver.cbl and
      * modernization/harness/run_harness.sh stand in the tree, every
      * run of the harness regenerates the tree
      * modernization/harness/build/, and the translated LGAPVS01 the
      * translator produces is compiled and executed from it. Every
      * statement below about the harness, about the translated program
      * or about the driver describes the delivered contract.
      *
      * Caller: the translated LGAPVS01 reaches the command site with
      * the request-type letter, the customer number and the policy
      * number already moved into the key at
      * base/src/lgapvs01.cbl:99-101. A captured key carries 'M' for
      * request id '01AMOT' and 'C' for '01ACOM'.
      *
      * Arity: six parameters, matching the six operands the generated
      * call supplies, in the order the source command states them.
      * The file name, the record, the two lengths and the key are
      * read; the response is the one parameter this module sets. Each
      * of the five read operands is recorded as received, so the
      * capture reports what the command supplied and not a value of
      * this module's own.
      *
      * No data set is reached. This module declares no file, names no
      * data-set path and alters nothing beyond the capture items
      * listed below.
      *
      * Response returned: HC-INJECT-VSAM-RESP at zero returns the
      * normal response condition, which the translated LGAPVS01
      * compares equal at base/src/lgapvs01.cbl:142 and continues with
      * CA-RETURN-CODE unchanged. A non-zero HC-INJECT-VSAM-RESP is
      * returned as it stands and HC-INJECT-VSAM-RESP2 is placed in
      * EIBRESP2, which that program reads at
      * base/src/lgapvs01.cbl:143 before it moves '80' to
      * CA-RETURN-CODE at base/src/lgapvs01.cbl:144. Both paths record
      * the record image, the key operand, the file name and the two
      * lengths: the command was issued either way.
      *
      * Chain witness: HC-CHAIN-VSAM-PRESENT becomes 'Y' and
      * HC-CHAIN-VSAM-CALEN receives EIBCALEN as observed inside the
      * translated LGAPVS01, the program that issues this command and
      * the one the translated LGAPDB01 links with LENGTH(32500) at
      * base/src/lgapdb01.cbl:243-246.
      *
      * Order guard: this command has two predecessors, both in the
      * program that links to it. The translated LGAPDB01 performs
      * INSERT-POLICY at base/src/lgapdb01.cbl:219 and one product
      * insert through the routing at base/src/lgapdb01.cbl:223-241
      * before the link at base/src/lgapdb01.cbl:243-246, the only
      * path that reaches this command. HC-POL-SEQ carries the first
      * predecessor and HC-MOT-SEQ, HC-COM-SEQ, HC-END-SEQ and
      * HC-HOU-SEQ carry the second, one of which the routing stamps.
      * This module reads all five after stamping its own ordinal: a
      * HC-POL-SEQ still at zero, or all four product ordinals still
      * at zero, reports the missing predecessor in
      * HC-ORDER-VIOLATION and HC-ORDER-VIOLATION-STMT. A captured
      * policy insert and a captured product insert leave both items
      * as modernization/harness/driver.cbl set them. The record and
      * the response are recorded either way: the command was issued
      * whatever the order.
      *
      * Capture surface, all declared by
      * modernization/harness/copybooks/hcapture.cpy: HC-VSAM-RECORD
      * and its nested items, HC-VSAM-RIDFLD and its nested items,
      * HC-VSAM-FILE, HC-VSAM-RECORD-LEN, HC-VSAM-KEY-LEN,
      * HC-VSAM-RESP, HC-VSAM-PRESENT, HC-VSAM-COUNT, HC-VSAM-SEQ,
      * HC-CHAIN-VSAM-PRESENT, HC-CHAIN-VSAM-CALEN, and the three
      * shared items HC-EVENT-SEQ, HC-ORDER-LAST-STMT and, on the
      * reported path of the order guard, HC-ORDER-VIOLATION with
      * HC-ORDER-VIOLATION-STMT. HC-INJECT-VSAM-RESP,
      * HC-INJECT-VSAM-RESP2 and the five ordinal items the order
      * guard reads are read here and never written. No
      * other item of that group is written: the SQL, seed, abend and
      * diagnostic-link items keep the values their
      * own owners set. Of
      * modernization/harness/copybooks/dfheiblk.cpy, EIBCALEN is read
      * on every call and EIBRESP2 is written on the injected-failure
      * path alone.
      *
      * Rationale belongs to modernization/docs/decision-log.md
      * (planned deliverable; not present at this milestone), rows:
      * flat VSAM payload capture; Ridfld operand captured apart from
      * the record image; normal-response constant representation;
      * deterministic failure injection through shared harness state;
      * chain traversal witnessed through the emulated services;
      * shared EXTERNAL harness state; uniform stub-side capture-order
      * guard.
      *
      * Harness topology: Figure 5 — Validation Harness Control Flow
      * in modernization/docs/architecture.md.
      *
      ******************************************************************
       IDENTIFICATION DIVISION.
       PROGRAM-ID. CICS-WRITE.
       ENVIRONMENT DIVISION.
       CONFIGURATION SECTION.
      *
       DATA DIVISION.
       WORKING-STORAGE SECTION.
      *
      *----------------------------------------------------------------*
      * Local constants of the emulated command. The file name and     *
      * the two lengths the command states are received as parameters  *
      * and are not held here.                                         *
      *----------------------------------------------------------------*
      * Value of the CICS NORMAL response condition. Returned through
      * the response parameter and recorded in HC-VSAM-RESP while
      * HC-INJECT-VSAM-RESP holds zero.
       77  WS-RESP-NORMAL       PIC S9(8) COMP VALUE +0.
      *
      * Name this module reports as the statement captured most
      * recently, moved into HC-ORDER-LAST-STMT.
       77  WS-STMT-NAME         PIC X(10) VALUE 'cics_write'.
      *
      *----------------------------------------------------------------*
      * Shared harness capture state. The group carries the EXTERNAL   *
      * clause. This module addresses the same storage as the driver   *
      * and as every other capture stub of the run unit.               *
      *----------------------------------------------------------------*
       COPY HCAPTURE.
      *
      *----------------------------------------------------------------*
      * Shared EXEC Interface Block surrogate. EIBCALEN is read as the *
      * COMMAREA length in force inside the translated LGAPVS01;       *
      * EIBRESP2 receives the injected secondary code when the         *
      * response returned is not the normal one.                       *
      *----------------------------------------------------------------*
       COPY DFHEIBLK.
      *
      ******************************************************************
      *    L I N K A G E     S E C T I O N
      ******************************************************************
       LINKAGE SECTION.
      *
      * Parameter 1, read. The data-set name supplied as
      * File('KSDSPOLY') at base/src/lgapvs01.cbl:135. Moved into
      * HC-VSAM-FILE. This module never assigns to it.
       01  LK-FILE-NAME              PIC X(8).
      *
      * Parameter 2, read. The 64-byte record image supplied as
      * From(WF-Policy-Info) at base/src/lgapvs01.cbl:136. Moved into
      * HC-VSAM-RECORD, which fills HC-VSAM-REQUEST-ID,
      * HC-VSAM-CUSTOMER-NUM, HC-VSAM-POLICY-NUM and
      * HC-VSAM-POLICY-DATA by position. This module never assigns to
      * it.
       01  LK-POLICY-INFO            PIC X(64).
      *
      * Parameter 3, read. The record length supplied as Length(64) at
      * base/src/lgapvs01.cbl:137, received as five zero-padded
      * digits. Moved into HC-VSAM-RECORD-LEN. This module never
      * assigns to it.
       01  LK-RECORD-LENGTH          PIC 9(5).
      *
      * Parameter 4, read. The 21-byte key supplied as
      * Ridfld(WF-Policy-Key) at base/src/lgapvs01.cbl:138. Moved into
      * HC-VSAM-RIDFLD, which fills HC-RID-REQUEST-ID,
      * HC-RID-CUSTOMER-NUM and HC-RID-POLICY-NUM by position. This
      * module never assigns to it.
       01  LK-POLICY-KEY             PIC X(21).
      *
      * Parameter 5, read. The key length supplied as KeyLength(21) at
      * base/src/lgapvs01.cbl:139, received as five zero-padded
      * digits. Moved into HC-VSAM-KEY-LEN. This module never assigns
      * to it.
       01  LK-KEY-LENGTH             PIC 9(5).
      *
      * Parameter 6, set. The response supplied as RESP(WS-RESP) at
      * base/src/lgapvs01.cbl:140. Receives the normal response value
      * while HC-INJECT-VSAM-RESP holds zero and that item's value
      * otherwise. The translated LGAPVS01 compares it at
      * base/src/lgapvs01.cbl:142: an equal compare continues with
      * CA-RETURN-CODE unchanged, an unequal compare reads EIBRESP2 at
      * base/src/lgapvs01.cbl:143 and moves '80' to CA-RETURN-CODE at
      * base/src/lgapvs01.cbl:144.
       01  LK-RESP                   PIC S9(8) COMP.
      *
      *----------------------------------------------------------------*
      ******************************************************************
       PROCEDURE DIVISION USING LK-FILE-NAME
                                LK-POLICY-INFO
                                LK-RECORD-LENGTH
                                LK-POLICY-KEY
                                LK-KEY-LENGTH
                                LK-RESP.
      *
      *----------------------------------------------------------------*
       MAINLINE SECTION.
      *----------------------------------------------------------------*
      *
      * Record the 64-byte image. The move fills the three nested key
      * items and the 43-byte payload item by position, following the
      * declaration order at base/src/lgapvs01.cbl:27-29. The payload
      * is held as one field and is not decoded. HC-VSAM-RECORD
      * receives this move and no other, so it holds the From operand
      * of base/src/lgapvs01.cbl:136 as passed.
           MOVE LK-POLICY-INFO      TO HC-VSAM-RECORD
      *
      * Record the key operand in a group of its own. The move fills
      * HC-RID-REQUEST-ID, HC-RID-CUSTOMER-NUM and HC-RID-POLICY-NUM by
      * position and leaves HC-VSAM-RECORD untouched, so the Ridfld
      * operand of base/src/lgapvs01.cbl:138 and the record image
      * remain two independent readings of the command.
           MOVE LK-POLICY-KEY       TO HC-VSAM-RIDFLD
      *
      * Record the file name and the two lengths the command supplied,
      * each as received.
           MOVE LK-FILE-NAME        TO HC-VSAM-FILE
           MOVE LK-RECORD-LENGTH    TO HC-VSAM-RECORD-LEN
           MOVE LK-KEY-LENGTH       TO HC-VSAM-KEY-LEN
      *
      * Return the response this run selects and record the value
      * returned. Zero in HC-INJECT-VSAM-RESP returns the normal
      * response condition; any other value is returned as it stands
      * and HC-INJECT-VSAM-RESP2 reaches EIBRESP2 for the error path at
      * base/src/lgapvs01.cbl:142-147.
           IF HC-INJECT-VSAM-RESP = ZERO
               MOVE WS-RESP-NORMAL       TO LK-RESP
               MOVE WS-RESP-NORMAL       TO HC-VSAM-RESP
           ELSE
               MOVE HC-INJECT-VSAM-RESP  TO LK-RESP
               MOVE HC-INJECT-VSAM-RESP  TO HC-VSAM-RESP
               MOVE HC-INJECT-VSAM-RESP2 TO EIBRESP2
           END-IF
      *
      * Report the command as captured and count this execution.
           SET  HC-VSAM-CAPTURED    TO TRUE
           ADD  1                   TO HC-VSAM-COUNT
           END-ADD
      *
      * Report that the translated LGAPVS01 was entered and record the
      * COMMAREA length in force there, set from LENGTH(32500) at
      * base/src/lgapdb01.cbl:243-246.
           SET  HC-CHAIN-VSAM-ENTERED TO TRUE
           MOVE EIBCALEN            TO HC-CHAIN-VSAM-CALEN
      *
      * Stamp the execution ordinal from the shared event sequence and
      * report this module as the statement captured most recently.
           ADD  1                   TO HC-EVENT-SEQ
           END-ADD
           MOVE HC-EVENT-SEQ        TO HC-VSAM-SEQ
           MOVE WS-STMT-NAME        TO HC-ORDER-LAST-STMT
      *
      * Test the two prerequisites of this command, read after the
      * ordinal above was stamped. Both are captured in the program
      * that links here: it performs INSERT-POLICY at
      * base/src/lgapdb01.cbl:219 and one product insert at
      * base/src/lgapdb01.cbl:223-241 before the link at
      * base/src/lgapdb01.cbl:243-246, the only path that reaches this
      * command. A HC-POL-SEQ at zero, or four product ordinals all at
      * zero, reports the missing predecessor under this module's own
      * name. Both predecessors present leave HC-ORDER-VIOLATION and
      * HC-ORDER-VIOLATION-STMT holding the values the driver set.
           IF HC-POL-SEQ = ZERO
              OR (HC-MOT-SEQ = ZERO AND HC-COM-SEQ = ZERO
                  AND HC-END-SEQ = ZERO AND HC-HOU-SEQ = ZERO)
               MOVE 'Y'             TO HC-ORDER-VIOLATION
               MOVE WS-STMT-NAME    TO HC-ORDER-VIOLATION-STMT
           END-IF.
      *
      *----------------------------------------------------------------*
       A-EXIT.
           GOBACK.
      *----------------------------------------------------------------*

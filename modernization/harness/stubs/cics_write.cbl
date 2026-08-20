      ******************************************************************
      *                                                                *
      *                       CICS-WRITE                               *
      *                                                                *
      *   VSAM write emulation for the GnuCOBOL validation harness     *
      *                                                                *
      ******************************************************************
      *
      * Emulates the one CICS write command of the Policy-Issue chain,
      * records what that command supplied in the shared harness
      * capture state and returns the normal response condition.
      *
      * Source construct : Write File('KSDSPOLY') command
      *                    base/src/lgapvs01.cbl:135-141
      * Record operand   : WF-Policy-Info, 64 bytes
      *                    base/src/lgapvs01.cbl:25-30
      * Key operand      : WF-Policy-Key, 21 bytes
      *                    base/src/lgapvs01.cbl:26-29
      * Response operand : WS-RESP
      *                    base/src/lgapvs01.cbl:18
      * Target module    : CICS-WRITE
      *
      * Milestone note: modernization/harness/translate.py, the
      * translated LGAPVS01 it produces, modernization/harness/
      * driver.cbl, modernization/harness/run_harness.sh and the
      * generated tree modernization/harness/build/ are planned
      * artifacts and are not present in the tree at this milestone;
      * every statement below about the harness, about the translated
      * program or about the driver is the planned contract.
      *
      * Caller: the translated LGAPVS01 reaches the command site with
      * the request-type letter, the customer number and the policy
      * number already moved into the key at
      * base/src/lgapvs01.cbl:99-101. A captured key carries 'M' for
      * request id '01AMOT' and 'C' for '01ACOM'.
      *
      * Arity: three parameters, matching the three operands the
      * generated call supplies. The record and the key are read; the
      * response is the one parameter this module sets.
      *
      * No data set is reached. This module declares no file, names no
      * data-set path and alters nothing beyond the capture items
      * listed below.
      *
      * Capture surface, all declared by
      * modernization/harness/copybooks/hcapture.cpy: HC-VSAM-RECORD
      * and its nested items, HC-VSAM-KEY, HC-VSAM-RECORD-LEN,
      * HC-VSAM-KEY-LEN, HC-VSAM-RESP, HC-VSAM-PRESENT, HC-VSAM-COUNT,
      * HC-VSAM-SEQ, and the two shared items HC-EVENT-SEQ and
      * HC-ORDER-LAST-STMT. No other item of that group is written:
      * the SQL, seed, abend, diagnostic-link and order-violation
      * items keep the values their own owners set.
      *
      * Rationale is recorded in modernization/docs/decision-log.md
      * (planned deliverable; not present at this milestone), rows:
      * flat VSAM payload capture; normal-response constant
      * representation; shared EXTERNAL harness state.
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
      * Literal properties of the emulated command. The source         *
      * command states each of these as a literal.                     *
      *----------------------------------------------------------------*
      * Data-set name, from File('KSDSPOLY') at
      * base/src/lgapvs01.cbl:135. Identifies the resource the
      * emulated command addresses.
       77  WS-VSAM-FILE-NAME    PIC X(8)  VALUE 'KSDSPOLY'.
      *
      * Record length, from Length(64) at base/src/lgapvs01.cbl:137.
      * Recorded in HC-VSAM-RECORD-LEN.
       77  WS-VSAM-RECORD-LEN   PIC 9(4)  VALUE 64.
      *
      * Key length, from KeyLength(21) at base/src/lgapvs01.cbl:139.
      * Recorded in HC-VSAM-KEY-LEN.
       77  WS-VSAM-KEY-LEN      PIC 9(4)  VALUE 21.
      *
      * Value of the CICS NORMAL response condition. Returned through
      * the response parameter and recorded in HC-VSAM-RESP on every
      * call.
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
      ******************************************************************
      *    L I N K A G E     S E C T I O N
      ******************************************************************
       LINKAGE SECTION.
      *
      * Parameter 1, read. The 64-byte record image supplied as
      * From(WF-Policy-Info) at base/src/lgapvs01.cbl:136. Moved into
      * HC-VSAM-RECORD, which fills HC-VSAM-REQUEST-ID,
      * HC-VSAM-CUSTOMER-NUM, HC-VSAM-POLICY-NUM and
      * HC-VSAM-POLICY-DATA by position. This module never assigns to
      * it.
       01  LK-POLICY-INFO            PIC X(64).
      *
      * Parameter 2, read. The 21-byte key supplied as
      * Ridfld(WF-Policy-Key) at base/src/lgapvs01.cbl:138. Moved into
      * HC-VSAM-KEY. This module never assigns to it.
       01  LK-POLICY-KEY             PIC X(21).
      *
      * Parameter 3, set. The response supplied as RESP(WS-RESP) at
      * base/src/lgapvs01.cbl:140. Receives the normal response value
      * on every call. The translated LGAPVS01 compares it at
      * base/src/lgapvs01.cbl:142 and continues with CA-RETURN-CODE
      * unchanged.
       01  LK-RESP                   PIC S9(8) COMP.
      *
      *----------------------------------------------------------------*
      ******************************************************************
       PROCEDURE DIVISION USING LK-POLICY-INFO
                                LK-POLICY-KEY
                                LK-RESP.
      *
      *----------------------------------------------------------------*
       MAINLINE SECTION.
      *----------------------------------------------------------------*
      *
      * Record the 64-byte image. The move fills the three nested key
      * items and the 43-byte payload item by position, following the
      * declaration order at base/src/lgapvs01.cbl:27-29. The payload
      * is held as one field and is not decoded.
           MOVE LK-POLICY-INFO      TO HC-VSAM-RECORD
      *
      * Record the key operand in its own right. Both operands address
      * the same 21 bytes at base/src/lgapvs01.cbl:26. This move
      * records the key the command supplied through Ridfld.
           MOVE LK-POLICY-KEY       TO HC-VSAM-KEY
      *
      * Record the two lengths the command states.
           MOVE WS-VSAM-RECORD-LEN  TO HC-VSAM-RECORD-LEN
           MOVE WS-VSAM-KEY-LEN     TO HC-VSAM-KEY-LEN
      *
      * Return the normal response condition and record the value
      * returned.
           MOVE WS-RESP-NORMAL      TO LK-RESP
           MOVE WS-RESP-NORMAL      TO HC-VSAM-RESP
      *
      * Report the command as captured and count this execution.
           SET  HC-VSAM-CAPTURED    TO TRUE
           ADD  1                   TO HC-VSAM-COUNT
      *
      * Stamp the execution ordinal from the shared event sequence and
      * report this module as the statement captured most recently.
      * This module has no declared prerequisite ordinal. It leaves
      * HC-ORDER-VIOLATION and HC-ORDER-VIOLATION-STMT holding the
      * values the driver set.
           ADD  1                   TO HC-EVENT-SEQ
           MOVE HC-EVENT-SEQ        TO HC-VSAM-SEQ
           MOVE WS-STMT-NAME        TO HC-ORDER-LAST-STMT.
      *
      *----------------------------------------------------------------*
       A-EXIT.
           GOBACK.
      *----------------------------------------------------------------*

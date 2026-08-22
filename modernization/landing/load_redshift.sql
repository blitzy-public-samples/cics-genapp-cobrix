-- load_redshift.sql
-- Real-target raw loader for the GenApp Policy-Issue cloud-warehouse bridge.
-- Loads the one landed Amazon S3 object into raw.genapp_policy_issue on Amazon Redshift.
-- The counterpart loader is modernization/landing/load_local.py, which reads the same
-- object and writes the same 17 columns, in the same order, into the same relation on
-- the local DuckDB target. The statements below carry that loader's semantics onto the
-- real target: one validated object, one staged row, one natural key removed, one row
-- written, one transaction, and a rollback that leaves the relation as it was found.
--
-- Run order. modernization/warehouse/ddl/01_schemas.sql provides the raw schema and
-- modernization/warehouse/ddl/02_raw_genapp_policy_issue.sql defines the relation and
-- owns its column widths. This file reads one object and writes one row. Apart from the
-- transient staging relation it creates and drops inside its own transaction, it
-- defines, alters and drops nothing, and it provisions no AWS resource of any kind.
--
-- =============================================================================
-- EXECUTION CONTRACT. These statements are not a text template. They are sent by
-- a client that binds parameters, and a caller that expands text and sends the
-- result unbound is refused by Amazon Redshift before any row moves.
-- =============================================================================
--
-- (1) BOUND VALUES. Every value Amazon Redshift can bind is a parameter marker and is
--     never joined into statement text. The pinned client is redshift-connector 2.1.16
--     (modernization/requirements.txt) with redshift_connector.paramstyle set to
--     "pyformat", so a marker is written %(name)s. Two markers appear below:
--       %(source_system_key)s  source_system_key of the validated landing record
--       %(policy_number)s      policy_number of the validated landing record
--     Both values are read from the validated record itself, never from the environment
--     and never parsed back out of the object key. Every statement carrying a marker is
--     executed with the mapping holding both names; every statement carrying none is
--     executed with no parameter argument. A marker left unbound is not valid Amazon
--     Redshift syntax, so a text-substitution pass over this file fails closed.
--
-- (2) SUBSTITUTION TOKENS. Amazon Redshift binds no parameter inside a COPY location,
--     an IAM_ROLE, a REGION or a SET value, so those four positions carry
--     placeholder tokens, each written as a dollar sign, a brace, the name and a
--     closing brace.
--     Before substituting a token the executor matches its value against the anchored
--     pattern named for it here and rejects the load, sending no statement, when the
--     value does not match. Each pattern is anchored \A to \Z, the anchors
--     modernization/landing/land_to_s3.py applies to the same key segments, so the whole
--     value is matched and a trailing newline is not admitted. No value these patterns
--     accept can contain a quote, a backslash, whitespace or a semicolon, so no accepted
--     value can close the literal it is substituted into or add a statement. Every token
--     but ${STATEMENT_TIMEOUT_MS} is substituted inside a quoted literal; that one is
--     digits alone.
--       ${S3_BUCKET}             \A[A-Za-z0-9_.\-]{3,63}\Z
--                                bucket holding the landed object
--       ${SOURCE_SYSTEM_KEY}     \A[A-Za-z0-9_.\-]{1,64}\Z
--                                source-system segment of the landed object key, equal
--                                to the record's own source_system_key value, which
--                                modernization/landing/landing-schema.json holds to
--                                this same shape
--       ${EXTRACT_DATE}          \A[0-9]{4}-[0-9]{2}-[0-9]{2}\Z
--                                extract-date segment of the landed object key, and a
--                                real calendar date
--       ${REDSHIFT_IAM_ROLE}     \Aarn:aws[a-z\-]*:iam::[0-9]{12}:role/[A-Za-z0-9+=,.@_/\-]{1,512}\Z
--                                role authorising this load to read that bucket
--       ${AWS_REGION}            \A[a-z]{2}(-[a-z]+){1,3}-[0-9]\Z
--                                region of that bucket
--       ${STATEMENT_TIMEOUT_MS}  \A[1-9][0-9]{0,8}\Z
--                                milliseconds any one statement of this load may run
--                                before Amazon Redshift cancels it; the executor
--                                supplies 900000 when the caller names no value, and
--                                the pattern admits no 0, which would remove the bound
--     The entity segment of the object key is the literal policy_issue below and is not
--     a token. No other position of this file is substituted.
--
-- (3) CLIENT-SIDE VALIDATION, completed before the first statement is sent. The
--     executor downloads exactly the object named in contract item (4) and admits it
--     under the contract modernization/landing/load_local.py applies to the same object
--     on the local target: the complete Draft 2020-12 schema
--     modernization/landing/landing-schema.json, that loader's rejection of ambiguous
--     JSON, its semantic date, timestamp and landable-stage checks, and equality
--     between the object key read and the key rebuilt from the record's own
--     source_system_key, the literal entity policy_issue and the extract date. A record
--     failing any of those checks is reported and no statement below is sent. The schema
--     requires all 17 keys and admits no eighteenth, so a record that reaches the COPY
--     carries every landed key and nothing else, and the object the executor validated is
--     the object the COPY reads.
--
-- (4) EXACT OBJECT. The COPY below names a one-entry manifest, so exactly the one
--     validated object is read and no sibling key sharing its prefix is loaded.
--     modernization/landing/land_to_s3.py writes that manifest beside the landed
--     object, in the same landing run and after the object itself, at the landing
--     prefix with the object name replaced:
--       landing/source_system_key=<key>/entity=policy_issue/extract_date=<date>/part-0000.manifest.json
--     The manifest holds one JSON object naming one entry, whose url is the validated
--     object, whose mandatory flag is true and whose content_length is the byte count
--     of that object, so an absent object and an object of any other length both fail
--     the COPY instead of loading nothing:
--       {"entries":[{"url":"s3://<bucket>/landing/source_system_key=<key>/entity=policy_issue/extract_date=<date>/part-0000.json","mandatory":true,"content_length":<bytes>}]}
--     The url and the manifest key are built from the same validated components as the
--     COPY location below, and
--       modernization/landing/land_to_s3.py --render-redshift-load manifest --record <record>
--     prints the same document byte for byte for the same record, so the shipped order
--     is: land the record, apply the two warehouse DDL scripts, then run these
--     statements. The manifest is one of the two objects the landing prefix holds and
--     is left in place, so this load reads it without an executor writing anything to
--     the bucket; removing it belongs to whatever retention the landing prefix is
--     given, never to this load.
--
-- (5) STATEMENT ORDER AND FAILURE HANDLING. The statements are sent in the order
--     written, over one session whose autocommit is enabled and which is therefore not
--     already inside a transaction, so the BEGIN and COMMIT below delimit the unit of
--     work. Each assertion divides by a value counted from a scan of the relation it
--     names: a violated assertion divides by zero, Amazon Redshift raises the error, and
--     the transaction is aborted. On any error, and on an interruption, the executor
--     sends ROLLBACK, which also removes the staging relation, and reports which
--     statement failed and which assertion did not hold, naming no credential and no
--     role identifier. No row reaches raw.genapp_policy_issue unless every assertion
--     passed and the COMMIT succeeded.
--
-- Column contract. The column names and the column order below match the 17 keys of
-- modernization/landing/landing-schema.json, ordered by the landing.field_order block
-- of modernization/extraction/copybook_field_map.yml. Every target column is VARCHAR
-- and accepts null, and this load stores each landed value as the string that was
-- landed. All typing is performed by the dbt models downstream. A JSON null lands as
-- SQL NULL. A premium that does not apply to the policy type stays null, and never
-- becomes an empty string or a zero.
--
-- Natural key used by the loaders: (source_system_key, policy_number). This load takes
-- that key from the landed record and never from a separately supplied value: the object
-- is copied into the staging relation first, the staged record is accepted only when the
-- staging relation holds exactly one row whose key is present, well formed and equal to
-- the source_system_key= segment of the object that was read, and the delete and the
-- insert then both key on that staged value. The policy number is assigned once per
-- issued policy by the chain: the policy insert supplies DEFAULT for POLICYNUMBER at
-- base/src/lgapdb01.cbl:279 and the assigned value is recovered by IDENTITY_VAL_LOCAL at
-- base/src/lgapdb01.cbl:308-311.
--
-- Privileges this load uses: TEMP on the database for the staging relation, and SELECT,
-- DELETE and INSERT on raw.genapp_policy_issue. It needs no privilege on any other
-- relation, schema or database.
--
-- Execution status. Authored, not executed. No Amazon Redshift cluster or workgroup and
-- no AWS access is available on this branch, and these statements have never been run
-- against a real target, so formal AWS validation of this loader remains OPEN. Results
-- obtained through modernization/landing/load_local.py are local-substitute results and
-- close nothing here. modernization/validation/validation-evidence.md will record that
-- status; it is a planned deliverable and is not present at this milestone.
--
-- Substitution. The only supported substitution path for the placeholder tokens in
-- this file is
--     modernization/landing/land_to_s3.py --render-redshift-load sql --record <record>
-- Hand substitution and any other renderer are unsupported. That renderer reads the
-- landed record, validates it against modernization/landing/landing-schema.json, and
-- before substituting anything it validates every value against the per-placeholder
-- allowlist recorded below, refuses a value carrying a control character, a newline, a
-- semicolon, a quote, a backslash or a SQL comment sequence, doubles any single quote a
-- value would carry into a SQL string literal, refuses a placeholder in this template
-- that is not on the allowlist, and refuses a placeholder it holds no value for. It
-- then refuses to emit anything unless the object key rendered below is exactly the key
-- the record's own source_system_key with the run's entity and extract date produce,
-- the policy number rendered below is exactly the record's own policy_number, the COPY
-- column list is exactly the 17 landed column names in the landing order, the rendered
-- text carries no remaining placeholder token, and its statement sequence is the
-- authored one: SET, BEGIN, CREATE, COPY, SELECT, SELECT, DELETE, INSERT, SELECT, DROP,
-- COMMIT, with every statement between the opening BEGIN and the closing COMMIT and
-- exactly one COPY and one DELETE among them. The delete is keyed by the two bound
-- markers %(source_system_key)s and %(policy_number)s named in the execution contract
-- above, not by substituted text. No secret, account identifier, role identifier,
-- bucket name, endpoint or region literal is written into this file.
--
-- Placeholders and the allowlist each value is validated against. Each name below
-- stands for the token written as a dollar sign, a brace, the name and a closing brace
-- in the statements further down:
--   S3_BUCKET              bucket holding the landed object: 3 to 63 characters of
--                          ASCII lower-case letters, digits, dot and hyphen, starting
--                          and ending with a letter or digit, with no consecutive dots
--                          and not written as an IPv4 address
--   SOURCE_SYSTEM_KEY      source-system discriminator of the landed record, and the
--                          first key=value segment of the landed object key: 1 to 64
--                          characters of ASCII letters, digits, underscore, dot and
--                          hyphen
--   ENTITY                 entity name segment of the landed object key, under the
--                          same shape as SOURCE_SYSTEM_KEY
--   EXTRACT_DATE           extract date segment of the landed object key: a real
--                          calendar date written YYYY-MM-DD
--   POLICY_NUMBER          policy number of the landed record, matched by the delete
--                          guard below: 1 to 10 digits, the width of CA-POLICY-NUM
--                          PIC 9(10), base/src/lgcmarea.cpy:35
--   REDSHIFT_IAM_ROLE      IAM role that authorises this load to read the bucket,
--                          written as an ARN: arn, the aws partition, iam, twelve
--                          account digits and role/ followed by 1 to 512 characters of
--                          the IAM role path and name character set
--   AWS_REGION             region of the S3 bucket named above, written as an AWS
--                          region code such as eu-west-2
--   OBJECT_CONTENT_LENGTH  byte count of the validated landed object: 1 to 12 digits
--                          with no leading zero
--   OBJECT_SHA256          SHA-256 digest of that object's bytes: 64 lower-case hex
--                          characters
--   OBJECT_ETAG            ETag of that object: 32 lower-case hex characters,
--                          optionally followed by a hyphen and a part count
--   OBJECT_VERSION_ID      version id of that object on a versioned bucket: 1 to 1024
--                          characters of ASCII letters, digits, dot, underscore and
--                          hyphen, or the literal not-versioned when the bucket keeps
--                          no versions
--
-- Object binding. The COPY below reads a manifest rather than the object key directly,
-- so the load is bound to the object that was validated instead of to whatever object
-- currently sits at the key. That manifest is already on the bucket: a successful
--     modernization/landing/land_to_s3.py --record <record>
-- writes it as part-0000.manifest.json beside the record under the same landing prefix,
-- with one entry carrying the landed object's URL, "mandatory": true and
-- "content_length" set to the byte count recorded below, so a replaced object of any
-- other length fails the COPY and a removed object fails it rather than loading
-- nothing. The same document, byte for byte, is printed by
--     modernization/landing/land_to_s3.py --render-redshift-load manifest --record <record>
-- for reading it without an S3 request. Confirm the recorded identity below against
--     aws s3api head-object --bucket ${S3_BUCKET} --key <key>
-- before running these statements; ETag, version id and byte count must all match, and
-- the SHA-256 digest is the digest of the bytes the landing step validated.
--
-- Validated object bound to this load:
--   key        landing/source_system_key=${SOURCE_SYSTEM_KEY}/entity=${ENTITY}/extract_date=${EXTRACT_DATE}/part-0000.json
--   bytes      ${OBJECT_CONTENT_LENGTH}
--   sha256     ${OBJECT_SHA256}
--   etag       ${OBJECT_ETAG}
--   version    ${OBJECT_VERSION_ID}
--   policy     ${POLICY_NUMBER}, the policy_number the validated record carries. The
--              delete guard below binds that value as a parameter rather than
--              substituting it, so it reaches no statement text.
--
-- Diagram reference: Figure 2 — AFTER (BUILT): Canonical Warehouse Bridge, in
-- modernization/docs/architecture.md.
-- Rationale for every choice in this file: modernization/docs/decision-log.md
-- (planned deliverable; not present at this milestone)

-- Statement 1 of 11. Bounds every statement of this load, including the COPY, for the
-- remainder of the session. Amazon Redshift cancels a statement that exceeds the value.
SET statement_timeout TO ${STATEMENT_TIMEOUT_MS};

-- Statement 2 of 11. Opens the one transaction that carries the load. Every statement
-- through the COMMIT below either takes effect together or leaves no trace.
BEGIN;

-- Statement 3 of 11. Staging relation, holding the copied object alone. LIKE takes the
-- column names, order, types and widths from raw.genapp_policy_issue, so this file
-- restates no column type and adds no column of its own. The relation is temporary and
-- visible to this session only: it disappears at the DROP below, at the ROLLBACK of a
-- failed load, or when the session ends, and a concurrent load on another session
-- stages into its own.
CREATE TEMPORARY TABLE genapp_policy_issue_load (LIKE raw.genapp_policy_issue);

-- Load the landed object through the manifest that names it, its byte count and its
-- mandatory presence. The 17 target columns are named explicitly, in the order fixed by
-- the landing contract. JSON 'auto' matches each lowercase object key of the landed
-- record to the column of the same name, so only these 17 columns can receive a value
-- and no other column of the relation is written.
-- The four commercial peril codes at base/src/lgcmarea.cpy:84, 86, 88 and 90 are not
-- landed fields and have no column here.
COPY genapp_policy_issue_load (
    -- Source-system discriminator assigned by the warehouse. No COBOL source item.
    source_system_key,
    -- CA-POLICY-NUM PIC 9(10), base/src/lgcmarea.cpy:35.
    policy_number,
    -- DB2-POLICYTYPE PIC X, base/src/lgpolicy.cpy:43, derived from CA-REQUEST-ID
    -- routing at base/src/lgapdb01.cbl:184-207.
    policy_type,
    -- CA-CUSTOMER-NUM PIC 9(10), base/src/lgcmarea.cpy:12.
    customer_number,
    -- CA-REQUEST-ID PIC X(6), base/src/lgcmarea.cpy:10.
    request_id,
    -- CA-RETURN-CODE PIC 9(2), base/src/lgcmarea.cpy:11.
    return_code,
    -- CA-ISSUE-DATE PIC X(10), base/src/lgcmarea.cpy:38.
    issue_date,
    -- CA-EXPIRY-DATE PIC X(10), base/src/lgcmarea.cpy:39.
    expiry_date,
    -- CA-LASTCHANGED PIC X(26), base/src/lgcmarea.cpy:40, read back at
    -- base/src/lgapdb01.cbl:315-321 and normalised to ISO-8601 by the extractor.
    last_changed,
    -- CA-BROKERID PIC 9(10), base/src/lgcmarea.cpy:41.
    broker_id,
    -- CA-BROKERSREF PIC X(10), base/src/lgcmarea.cpy:42.
    brokers_reference,
    -- CA-PAYMENT PIC 9(6), base/src/lgcmarea.cpy:43, moved unchanged at
    -- base/src/lgapdb01.cbl:265. Carried for every policy type.
    payment_amount,
    -- CA-M-PREMIUM PIC 9(6), base/src/lgcmarea.cpy:73, moved unchanged at
    -- base/src/lgapdb01.cbl:445. Populated on motor rows only, null otherwise.
    motor_premium_amount,
    -- CA-B-FirePremium PIC 9(8), base/src/lgcmarea.cpy:85, moved unchanged at
    -- base/src/lgapdb01.cbl:489. Populated on commercial rows only, null otherwise.
    fire_premium_amount,
    -- CA-B-CrimePremium PIC 9(8), base/src/lgcmarea.cpy:87, moved unchanged at
    -- base/src/lgapdb01.cbl:491. Populated on commercial rows only, null otherwise.
    crime_premium_amount,
    -- CA-B-FloodPremium PIC 9(8), base/src/lgcmarea.cpy:89, moved unchanged at
    -- base/src/lgapdb01.cbl:493. Populated on commercial rows only, null otherwise.
    flood_premium_amount,
    -- CA-B-WeatherPremium PIC 9(8), base/src/lgcmarea.cpy:91, moved unchanged at
    -- base/src/lgapdb01.cbl:495. Populated on commercial rows only, null otherwise.
    weather_premium_amount
)
FROM 's3://${S3_BUCKET}/landing/source_system_key=${SOURCE_SYSTEM_KEY}/entity=${ENTITY}/extract_date=${EXTRACT_DATE}/part-0000.manifest.json'
IAM_ROLE '${REDSHIFT_IAM_ROLE}'
FORMAT AS JSON 'auto'
MANIFEST
REGION '${AWS_REGION}';

-- Statement 5 of 11. Assertion: the COPY staged exactly one row. A staged count of
-- anything but 1 divides by zero and aborts the transaction, so neither a second object
-- nor an empty load can reach raw.genapp_policy_issue. The count comes from a scan of
-- the staging relation and is not known before the COPY has run.
SELECT 1 / CASE WHEN staged.staged_row_count = 1 THEN 1 ELSE 0 END
           AS assert_exactly_one_staged_row
  FROM (SELECT COUNT(*) AS staged_row_count FROM genapp_policy_issue_load) AS staged;

-- Statement 6 of 11. Assertion: the staged row carries the natural key of the record the
-- executor validated. With statement 5 already proving one staged row, an agreeing count
-- of 1 proves that row is that record; any other count divides by zero and aborts the
-- transaction. Both compared values are bound, not substituted.
SELECT 1 / CASE WHEN staged.agreeing_row_count = 1 THEN 1 ELSE 0 END
           AS assert_staged_natural_key_agrees_with_validated_record
  FROM (SELECT COUNT(*) AS agreeing_row_count
          FROM genapp_policy_issue_load
         WHERE source_system_key = %(source_system_key)s
           AND policy_number = %(policy_number)s) AS staged;

-- Statement 7 of 11. Delete guard, keyed on the natural key (source_system_key,
-- policy_number). Matches only the record this load is about to write. Every other
-- landed record keeps its row, and loading the same record again leaves exactly one row
-- for it.
-- The policy number is assigned once per issued policy by the chain: the policy insert
-- supplies DEFAULT for POLICYNUMBER at base/src/lgapdb01.cbl:279 and the assigned value
-- is recovered by IDENTITY_VAL_LOCAL at base/src/lgapdb01.cbl:308-311.
DELETE FROM raw.genapp_policy_issue
 WHERE source_system_key = %(source_system_key)s
   AND policy_number = %(policy_number)s;

-- Statement 8 of 11. Writes the staged row into the raw relation, naming all 17 columns
-- on both sides in the landing order of the COPY above. The values written are the
-- values the object carried: nothing is computed, scaled, trimmed, defaulted or
-- backfilled here, and a null stays null.
INSERT INTO raw.genapp_policy_issue (
    source_system_key,
    policy_number,
    policy_type,
    customer_number,
    request_id,
    return_code,
    issue_date,
    expiry_date,
    last_changed,
    broker_id,
    brokers_reference,
    payment_amount,
    motor_premium_amount,
    fire_premium_amount,
    crime_premium_amount,
    flood_premium_amount,
    weather_premium_amount
)
SELECT
    source_system_key,
    policy_number,
    policy_type,
    customer_number,
    request_id,
    return_code,
    issue_date,
    expiry_date,
    last_changed,
    broker_id,
    brokers_reference,
    payment_amount,
    motor_premium_amount,
    fire_premium_amount,
    crime_premium_amount,
    flood_premium_amount,
    weather_premium_amount
  FROM genapp_policy_issue_load;

-- Statement 9 of 11. Assertion: the raw relation now holds exactly one row for this
-- natural key. A count of anything but 1 divides by zero and aborts the transaction, so
-- a partial delete or a duplicated write is never committed. The count comes from a scan
-- of raw.genapp_policy_issue after the write.
SELECT 1 / CASE WHEN promoted.promoted_row_count = 1 THEN 1 ELSE 0 END
           AS assert_exactly_one_raw_row_for_natural_key
  FROM (SELECT COUNT(*) AS promoted_row_count
          FROM raw.genapp_policy_issue
         WHERE source_system_key = %(source_system_key)s
           AND policy_number = %(policy_number)s) AS promoted;

-- Statement 10 of 11. Removes the staging relation this transaction created.
DROP TABLE genapp_policy_issue_load;

-- Statement 11 of 11. Makes the load visible. Reached only when every statement above
-- succeeded and every assertion passed.
COMMIT;

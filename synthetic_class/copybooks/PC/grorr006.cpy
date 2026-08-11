******************************************************************
*  COPYBOOK  : GRORR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Products and Completed Operations Liability (PC)
*  STATE     : OR
******************************************************************
 01  RT-ROR-RATING.

          03 RT-ROR-TERRITORY-CODE            PIC X(3).
          03 RT-ROR-CLASS-CODE                PIC X(4).
          03 RT-ROR-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-ROR-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-ROR-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-ROR-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-ROR-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-ROR-RATED-PREMIUM             PIC 9(9)V9(2).

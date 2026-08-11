******************************************************************
*  COPYBOOK  : GUORR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Umbrella and Excess Liability (UM)
*  STATE     : OR
******************************************************************
 01  RT-UOR-RATING.

          03 RT-UOR-TERRITORY-CODE            PIC X(3).
          03 RT-UOR-CLASS-CODE                PIC X(4).
          03 RT-UOR-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-UOR-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-UOR-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-UOR-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-UOR-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-UOR-RATED-PREMIUM             PIC 9(9)V9(2).

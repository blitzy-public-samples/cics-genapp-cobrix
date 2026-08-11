******************************************************************
*  COPYBOOK  : GHORR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : OR
******************************************************************
 01  RT-HOR-RATING.

          03 RT-HOR-TERRITORY-CODE            PIC X(3).
          03 RT-HOR-CLASS-CODE                PIC X(4).
          03 RT-HOR-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HOR-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HOR-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HOR-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HOR-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HOR-RATED-PREMIUM             PIC 9(9)V9(2).

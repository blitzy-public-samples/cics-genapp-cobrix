******************************************************************
*  COPYBOOK  : GAORR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Personal and Advertising Injury Liability (PA)
*  STATE     : OR
******************************************************************
 01  RT-AOR-RATING.

          03 RT-AOR-TERRITORY-CODE            PIC X(3).
          03 RT-AOR-CLASS-CODE                PIC X(4).
          03 RT-AOR-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-AOR-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-AOR-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-AOR-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-AOR-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-AOR-RATED-PREMIUM             PIC 9(9)V9(2).

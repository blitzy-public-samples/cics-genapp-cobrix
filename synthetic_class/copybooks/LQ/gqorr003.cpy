******************************************************************
*  COPYBOOK  : GQORR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : OR
******************************************************************
 01  RT-QOR-RATING.

          03 RT-QOR-TERRITORY-CODE            PIC X(3).
          03 RT-QOR-CLASS-CODE                PIC X(4).
          03 RT-QOR-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QOR-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QOR-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QOR-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QOR-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QOR-RATED-PREMIUM             PIC 9(9)V9(2).

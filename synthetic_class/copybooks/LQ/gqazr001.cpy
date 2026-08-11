******************************************************************
*  COPYBOOK  : GQAZR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : AZ
******************************************************************
 01  RT-QAZ-RATING.

          03 RT-QAZ-TERRITORY-CODE            PIC X(3).
          03 RT-QAZ-CLASS-CODE                PIC X(4).
          03 RT-QAZ-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QAZ-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QAZ-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QAZ-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QAZ-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QAZ-RATED-PREMIUM             PIC 9(9)V9(2).

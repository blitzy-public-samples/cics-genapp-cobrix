******************************************************************
*  COPYBOOK  : GQALR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Liquor Liability (LQ)
*  STATE     : AL
******************************************************************
 01  RT-QAL-RATING.

          03 RT-QAL-TERRITORY-CODE            PIC X(3).
          03 RT-QAL-CLASS-CODE                PIC X(4).
          03 RT-QAL-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-QAL-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-QAL-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-QAL-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-QAL-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-QAL-RATED-PREMIUM             PIC 9(9)V9(2).

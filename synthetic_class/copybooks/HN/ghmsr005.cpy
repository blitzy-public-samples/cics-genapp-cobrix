******************************************************************
*  COPYBOOK  : GHMSR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Hired and Non-Owned Auto Liability (HN)
*  STATE     : MS
******************************************************************
 01  RT-HMS-RATING.

          03 RT-HMS-TERRITORY-CODE            PIC X(3).
          03 RT-HMS-CLASS-CODE                PIC X(4).
          03 RT-HMS-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-HMS-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-HMS-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-HMS-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-HMS-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-HMS-RATED-PREMIUM             PIC 9(9)V9(2).

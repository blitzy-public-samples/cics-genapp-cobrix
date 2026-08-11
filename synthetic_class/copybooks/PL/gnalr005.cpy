******************************************************************
*  COPYBOOK  : GNALR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Limited Pollution Liability (PL)
*  STATE     : AL
******************************************************************
 01  RT-NAL-RATING.

          03 RT-NAL-TERRITORY-CODE            PIC X(3).
          03 RT-NAL-CLASS-CODE                PIC X(4).
          03 RT-NAL-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-NAL-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-NAL-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-NAL-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-NAL-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-NAL-RATED-PREMIUM             PIC 9(9)V9(2).

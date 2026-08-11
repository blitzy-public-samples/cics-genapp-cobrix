******************************************************************
*  COPYBOOK  : GPSDR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : SD
******************************************************************
 01  RT-PSD-RATING.

          03 RT-PSD-TERRITORY-CODE            PIC X(3).
          03 RT-PSD-CLASS-CODE                PIC X(4).
          03 RT-PSD-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PSD-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PSD-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PSD-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PSD-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PSD-RATED-PREMIUM             PIC 9(9)V9(2).

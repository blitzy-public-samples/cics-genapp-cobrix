******************************************************************
*  COPYBOOK  : GCALR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : AL
******************************************************************
 01  RT-CAL-RATING.

          03 RT-CAL-TERRITORY-CODE            PIC X(3).
          03 RT-CAL-CLASS-CODE                PIC X(4).
          03 RT-CAL-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CAL-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CAL-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CAL-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CAL-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CAL-RATED-PREMIUM             PIC 9(9)V9(2).

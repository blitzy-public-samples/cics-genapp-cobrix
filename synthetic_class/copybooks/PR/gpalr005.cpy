******************************************************************
*  COPYBOOK  : GPALR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : AL
******************************************************************
 01  RT-PAL-RATING.

          03 RT-PAL-TERRITORY-CODE            PIC X(3).
          03 RT-PAL-CLASS-CODE                PIC X(4).
          03 RT-PAL-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PAL-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PAL-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PAL-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PAL-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PAL-RATED-PREMIUM             PIC 9(9)V9(2).

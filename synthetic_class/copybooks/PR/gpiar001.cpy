******************************************************************
*  COPYBOOK  : GPIAR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : IA
******************************************************************
 01  RT-PIA-RATING.

          03 RT-PIA-TERRITORY-CODE            PIC X(3).
          03 RT-PIA-CLASS-CODE                PIC X(4).
          03 RT-PIA-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PIA-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PIA-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PIA-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PIA-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PIA-RATED-PREMIUM             PIC 9(9)V9(2).

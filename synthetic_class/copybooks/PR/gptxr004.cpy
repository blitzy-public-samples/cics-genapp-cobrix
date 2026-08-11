******************************************************************
*  COPYBOOK  : GPTXR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Premises and Operations Liability (PR)
*  STATE     : TX
******************************************************************
 01  RT-PTX-RATING.

          03 RT-PTX-TERRITORY-CODE            PIC X(3).
          03 RT-PTX-CLASS-CODE                PIC X(4).
          03 RT-PTX-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-PTX-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-PTX-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-PTX-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-PTX-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-PTX-RATED-PREMIUM             PIC 9(9)V9(2).

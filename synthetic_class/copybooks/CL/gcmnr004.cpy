******************************************************************
*  COPYBOOK  : GCMNR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Contractual Liability (CL)
*  STATE     : MN
******************************************************************
 01  RT-CMN-RATING.

          03 RT-CMN-TERRITORY-CODE            PIC X(3).
          03 RT-CMN-CLASS-CODE                PIC X(4).
          03 RT-CMN-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-CMN-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-CMN-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-CMN-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-CMN-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-CMN-RATED-PREMIUM             PIC 9(9)V9(2).

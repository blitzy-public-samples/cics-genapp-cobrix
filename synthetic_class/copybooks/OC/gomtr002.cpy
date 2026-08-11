******************************************************************
*  COPYBOOK  : GOMTR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : MT
******************************************************************
 01  RT-OMT-RATING.

          03 RT-OMT-TERRITORY-CODE            PIC X(3).
          03 RT-OMT-CLASS-CODE                PIC X(4).
          03 RT-OMT-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OMT-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OMT-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OMT-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OMT-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OMT-RATED-PREMIUM             PIC 9(9)V9(2).

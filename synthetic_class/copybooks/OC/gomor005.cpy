******************************************************************
*  COPYBOOK  : GOMOR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : MO
******************************************************************
 01  RT-OMO-RATING.

          03 RT-OMO-TERRITORY-CODE            PIC X(3).
          03 RT-OMO-CLASS-CODE                PIC X(4).
          03 RT-OMO-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OMO-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OMO-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OMO-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OMO-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OMO-RATED-PREMIUM             PIC 9(9)V9(2).

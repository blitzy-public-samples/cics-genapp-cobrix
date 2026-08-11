******************************************************************
*  COPYBOOK  : GOMER001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : ME
******************************************************************
 01  RT-OME-RATING.

          03 RT-OME-TERRITORY-CODE            PIC X(3).
          03 RT-OME-CLASS-CODE                PIC X(4).
          03 RT-OME-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OME-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OME-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OME-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OME-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OME-RATED-PREMIUM             PIC 9(9)V9(2).

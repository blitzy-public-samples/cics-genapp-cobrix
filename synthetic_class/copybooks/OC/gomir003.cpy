******************************************************************
*  COPYBOOK  : GOMIR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : MI
******************************************************************
 01  RT-OMI-RATING.

          03 RT-OMI-TERRITORY-CODE            PIC X(3).
          03 RT-OMI-CLASS-CODE                PIC X(4).
          03 RT-OMI-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OMI-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OMI-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OMI-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OMI-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OMI-RATED-PREMIUM             PIC 9(9)V9(2).

******************************************************************
*  COPYBOOK  : GOMNR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Owners and Contractors Protective Liability (OC)
*  STATE     : MN
******************************************************************
 01  RT-OMN-RATING.

          03 RT-OMN-TERRITORY-CODE            PIC X(3).
          03 RT-OMN-CLASS-CODE                PIC X(4).
          03 RT-OMN-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-OMN-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-OMN-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-OMN-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-OMN-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-OMN-RATED-PREMIUM             PIC 9(9)V9(2).
